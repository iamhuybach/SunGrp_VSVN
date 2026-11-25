RESULT: PASS

## Main brief

### Decision
- PASS. The init rerun is the Dev repair, because `legacy_upsert_sql` only updates rows with `load_origin='LEGACY_INIT'`. Every destination check runs before the first write. `destination_id` is `to_json(from_json(ids,'array<string>'))` from all mapped langs of one `poi_id`. Accepted shapes: NULL, `[]`, or all-string elements; any other shape, or any cross-lang disagreement, stops with USER_DECISION.
- Multi-lang `poi_name` comes from `poi_master.poi_name` of the legacy row behind each display row, so the lang matches. A name conflict sets it to NULL and counts it. The column goes right after `lang` in every layer.
- The pipeline writes a typed NULL for `poi_name` on P1 and P2. `row_hash` is unchanged because `to_json` drops nulls, so there is no mass rewrite.
- Workspace: `p_target_ws` must equal the running workspace. The `NB_CREATE_DDL` cells (`legacyidpy`, new `lgpnamepy`) resolve the running workspace themselves.
- Stop 1 (user): three files outside `scope.files` are needed. Without the entity and the legacy test file, `verify` fails.

### Invariants Main must preserve
- Init never updates rows with `load_origin` NULL. Only the LEGACY_INIT branch of `legacy_upsert_sql` updates.
- In RUN, the `USER_DECISION destination_ids` raise happens before `write_insert_only(MAP_FQ`.
- `lgpmain` has no `"$[0]"`. Every non-null init `destination_id` is a JSON array of strings, or `[]`.
- `destination_id` is set only when all mapped langs agree on the canonical string. NULL against non-NULL counts as disagreement.
- Multi-lang `poi_name` matches the name of a legacy row with the same lang, or is NULL. It is never copied from another lang.
- `ML_COLS` excludes `poi_name`. P1 and P2 emit a STRING NULL.
- `TARGET_WS` passes the regex, is not the old workspace, and equals `_workspace_name()`. Every write FQ starts with `TARGET_WS + "."`.
- A rerun with the same pin inserts 0 rows into map, info, and multi_lang, and changes no `poi_id`.
- Gold `TABLE_SPECS` equals the PostgreSQL columns minus `ingestion_ts`, which equals the entity columns minus `ingestion_ts`. `OUT_COLS` order equals `TABLE_SPECS` order, and `OUT_COLS[-1]` stays `experience`.
- Rollout order: PostgreSQL column, then service. Hibernate with `ddl-auto: none` fails if the entity maps a column that does not exist.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 0 | .ai/tasks/…/decision.md | Quyết định hiện hành | Add D-05 (§A Q1–4), D-06 (Q5–7), D-07 (workspace, `DICT_FQ`, legacyidpy, lgpnamepy), D-08 (scope ext.) | Rows exist before any code edit |
| 1 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | id:lgpmd | Text: target is `p_target_ws`; upsert of LEGACY_INIT rows | No `sgr_visitvn_dev` as the target |
| 2 | same | id:lgpparams | Add `p_target_ws = ""` | Present |
| 3 | same | id:lgpconst | Full doc "C2": `TARGET_WS` checks and f-string FQs, including `DICT_FQ` | No `sgr_visitvn_dev`; `OLD` unchanged |
| 4 | same | id:lgppure | Append `DEST_ACCEPT` and `destination_ids_shape` ("C1") | Pure test passes |
| 5 | same | id:lgpmain preflight + `write_insert_only` | "C3": workspace guard, write guard, `poi_name` and `destination_ids` type guards, `summary.target_ws` | Guards present |
| 6 | same | id:lgpmain after `map_rows =` | Insert the destination block ("C4") before the map write | Ordering test passes |
| 7 | same | id:lgpmain `master_rows` | "C5": drop `$[0]`; `master_cols` = `is_recommended`, `destination_name`; join `dest_one` before `n_before` | Test passes |
| 8 | same | id:lgpmain stage multi_lang | "C6": `names_src` join, `poi_name` in `picked` (not in `pay`), `name_one` join, two metrics | Test passes |
| 9 | notebooks/NB_CREATE_DDL.ipynb | id:legacyidpy | `WS` from `currentWorkspaceName`, with a raise if empty ("C7") | No literal dev name |
| 10 | same | after legacyidpy (end) | Append `lgpnamemd` + `lgpnamepy` verbatim ("C7") | Cell test passes |
| 11 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | id:init_tables `gld_srv_poi_multi_lang` cols | Add `('poi_name', 'STRING', None),` after `lang` | Contract tests pass |
| 12 | notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb | id:srvmlbuild | "C8": `OUT_COLS` with `poi_name` third; P1 `.withColumn("poi_name", F.lit(None).cast("string"))`; P2 `F.lit(None).alias("poi_name")`; keep the asserted lines byte-exact | gld_srv tests pass |
| 13 | same | id:srvmlmd | One line on the NULL `poi_name` and D-02 | — |
| 14 | sql/postgres/gld_srv_serve.pg.sql | header + `CREATE TABLE apps.srv_poi_multi_lang` | `--` ALTER comment line; `poi_name text,` after `lang` ("C9") | Serving test passes |
| 15 | docs/context/mapping_gld_srv_poi_multi_lang.md | §1.1, §1.2 | Bullet; row after `lang` containing `P2: null` ("C9") | `test_multi_lang_mapping_targets` passes |
| 16 | tests/test_srv_poi_serving_contract.py | `test_destination_name_patch_cell`; new test | `ids[-10:]` with lgpname cells; `test_multi_lang_poi_name_across_layers` ("C10") | Pass |
| 17* | services/.../entity/SrvPoiMultiLang.java | after `lang` field | `@Column(name = "poi_name") private String poiName;` with no DTO change | Entity test passes |
| 18* | tests/test_legacy_gold_poi_init_contract.py | tests named in "C10" | Update 3 dev-literal tests; add 4 new tests | Pass |
| 19* | docs/context/mapping_legacy_gold_to_gld_srv.md | line 3; §1 row 7; §2 | Target param; full array rule; 14 columns with `poi_name` | — |

(*) Only after Stop 1 approves.

### Order and stop points
1. **STOP (user decision):** approve the scope extension for rows 17–19 (recommended: all three). If the entity is rejected, stop; `verify` cannot pass. Record D-08 and extend `scope.files`.
2. Row 0 (`decision.md`), then rows 1–8, then 9–11, then 12–15, then 16–19.
3. Local verification (below). Fix P0 and P1 within the round cap.
4. `run-gate`, then specialist review (sql-data, spark-runtime, state-correctness), then the risk gate.
5. `run-author --kind runbook`, using full doc "Rollout" and "Verification" (runtime a–e). **STOP (waiting_runtime):** the user runs the Dev steps: PostgreSQL ALTER, lgpnamepy, service, PLAN, RUN, checks. Then Prod with the Prod workspace name the user supplies.
6. **STOP (user decision)** if PLAN shows `destination.decision = USER_DECISION`. Report `shape`, `stop_n`, `conflict_n`, and the samples. Make no code change before a decision is recorded.

### Tests and verification
- `python -m pytest tests/test_legacy_gold_poi_init_contract.py tests/test_srv_poi_serving_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest -q`
- `cd services/data-serving-service; .\mvnw.cmd -q -Dtest=PoiServiceTest test`. Record the Testcontainers integration tests as not run (they need Docker).
- `python scripts/vv.py verify 20261125-legacy-init-destination-and-poi-name`
- New tests:
  - `test_destination_ids_shape_classes`
  - `test_init_destination_full_array_before_writes`
  - `test_init_target_workspace_param` (replaces `test_init_write_targets_dev_only`)
  - `test_init_ml_poi_name_per_lang`
  - `test_poi_name_ddl_cell_contract`
  - `test_multi_lang_poi_name_across_layers`
- Updated tests: `test_legacy_upsert_updates_only_legacy_rows` (line 108), `test_legacyid_ddl_cell_contract`, `test_destination_name_patch_cell`.
- Must stay green unchanged: `test_build_columns_match_ddl`, `test_multi_lang_experience_rule`, `test_multi_lang_i18n_only_branch`, `test_multi_lang_mapping_targets`, `test_node_specs`, `test_gold_and_pg_columns_and_types_match`, `test_entities_match_gold_columns_types_and_keys`, `test_columns_match_sources`.

### Read only if needed
- "§A Answers to model-design questions": rows 0, 4, 6–8, 11–12.
- "§B Scope extension (Stop 1)": rows 17–19, Stop 1.
- "Invariants", "State ownership": rows 5–8, 12.
- "Ordering", "Transaction and commit boundaries", "Partial failure": rows 5–6, 10.
- "Concurrency": rows 9–10 (lock pattern).
- "Rollout", "Rollback and forward recovery": step 5 runbook.
- "Alternatives": the rationale for rows 6, 8, 11–12.
- "Implementation plan" C1–C10: code for rows 3–16 and the test specs.
- "Verification": runtime checks a–e for the runbook.

# Architecture: 20261125-legacy-init-destination-and-poi-name

Inputs: `model-design.md` (grain, keys, columns, lineage), ledger D-01..D-04, `evidence/results/destination_id_non_legacy_shape.txt` (verdict `keep_string`). There is no `proposal.md`. This document answers the ten questions in `model-design.md` `## Conflicts and questions` (see §A) and does not change the model.

One blocking item is a scope decision, not a data gap. The request's acceptance criteria force edits to three files outside `scope.files` (see §B). Main stops for a user decision before the first edit (Stop 1).

## Scope

- `NB_SETUP_LEGACY_GOLD_POI`:
  - Add the target-workspace parameter.
  - Classify `destination_ids` and stop on a bad shape or a cross-lang conflict before any write.
  - Write the full array as one JSON string.
  - Write per-lang `poi_name` on multi-lang rows.
  - A rerun in RUN mode is the Dev repair.
- `NB_CREATE_DDL`:
  - Add a new cell pair `lgpnamemd`/`lgpnamepy` that adds `poi_name` to an existing `gld_srv_poi_multi_lang`.
  - In `legacyidpy`, take the workspace from the running workspace instead of the hard-coded `sgr_visitvn_dev`, so Prod prep needs no notebook edit.
- `NB_SETUP_INITIAL_DDL` `init_tables`: add `poi_name STRING` after `lang`.
- `NB_GLD_SRV_POI_MULTI_LANG` `srvmlbuild`: write `poi_name` as a typed null on P1 and P2.
- `sql/postgres/gld_srv_serve.pg.sql`: add `poi_name text` to `apps.srv_poi_multi_lang`, plus a manual `ALTER` comment for existing databases.
- Docs: `mapping_gld_srv_poi_multi_lang.md`. If Stop 1 approves: `mapping_legacy_gold_to_gld_srv.md` and the JPA entity.
- Tests: `test_srv_poi_serving_contract.py`. If Stop 1 approves: `test_legacy_gold_poi_init_contract.py`.

## Non-goals

- No `ARRAY` type for `destination_id` (D-04). No change to `NB_GLD_SRV_POI_INFO` or to `destination_name`.
- `poi_name` is not added to the API JSON or DTOs. The entity field is persistence only.
- No `poi_name` on `gld_srv_poi_info` (base D-06 is unchanged).
- No new multi-lang rows from `poi_master` alone. Multi-lang rows are still driven by `poi_enrichment_display`.
- No change to `legacy_upsert_sql`, `insert_only_sql`, `sql_merge_target`, locks, or the pin mechanism.
- No Fabric or PostgreSQL execution from the agent session.

## §A Answers to model-design questions

| Q | Decision |
|---|---|
| 1 | The cross-lang check covers every `poi_master` row mapped (status `OK`) to the same new `poi_id`, across all langs, not only `vi`. If the langs agree, `destination_id` is set even when there is no `vi` row. |
| 2 | Python only classifies. Spark serializes the value with `to_json(from_json(destination_ids, 'array<string>'))`, the same serializer the pipeline's silver writer uses (`to_json` of the id array). The output is compact, keeps element order and duplicates, and does not change the text of each element. Conflicts are compared on this canonical string, so whitespace differences do not count but order differences do. |
| 3 | Old `[]` becomes `"[]"` (pipeline rows already have 2 of these). Old NULL stays NULL. |
| 4 | Classes: `NULL`, `EMPTY`, `STRINGS` are accepted. `NOT_JSON` (includes blank), `NOT_ARRAY`, `NULL_ELEMENT`, and `NON_STRING_ELEMENT` stop the run. A null element stops the run. |
| 5 | A `poi_name` conflict inside one `(poi_id, lang)` sets `poi_name` to NULL for that key. The row is still written with its content payload and counted in `name_conflict_n`. No name is picked, and existing multi-lang coverage does not shrink. |
| 6 | The name comes from the legacy row behind the display row: `poi_master.poi_id = display.poi_id = mp.legacy_poi_id`. Its lang is `mp.lang`, which is the target `lang`. |
| 7 | `poi_name` goes immediately after `lang`: in `TABLE_SPECS`, `OUT_COLS`, the Delta `ALTER ... AFTER lang`, and the PostgreSQL `CREATE TABLE`. Placing it after `experience` would break `test_multi_lang_experience_rule` (`OUT_COLS[-1] == "experience"`), and `test_build_columns_match_ddl` requires the `OUT_COLS` order to equal the `TABLE_SPECS` order. |
| 8 | Add the entity field `poiName` with `@Column(name = "poi_name")`. Do not touch DTOs. `PoiService` maps fields by hand, so the API JSON does not change. This needs Stop 1. |
| 9 | `DICT_FQ` and every write guard use the same `TARGET_WS`. `OLD` stays as it is. |
| 10 | `destination_name` stays unchanged (`vi` row, raw string). |

## §B Scope extension (Stop 1)

| File | Why it is forced | Without it |
|---|---|---|
| `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiMultiLang.java` | `test_entities_match_gold_columns_types_and_keys` runs because the service tree exists. Gold `TABLE_SPECS` gains `poi_name`, so the entity must gain it too. | `verify` fails. |
| `tests/test_legacy_gold_poi_init_contract.py` | `test_init_write_targets_dev_only`, line 108 of `test_legacy_upsert_updates_only_legacy_rows`, and `test_legacyid_ddl_cell_contract` assert the `sgr_visitvn_dev` literals that D-03 removes. New pure-function tests also belong here. | `verify` fails. |
| `docs/context/mapping_legacy_gold_to_gld_srv.md` | The init mapping says `destination_id` is the "first element" (row 7) and lists 13 multi-lang columns. | Docs are wrong. No test fails. |

Recommended: approve all three. Main records this as D-08 and extends `scope.files`. If the user rejects the entity edit, the task cannot pass `verify`; stop.

## Invariants

1. Init never updates a row where `load_origin` is NULL. Only `legacy_upsert_sql`'s `load_origin = 'LEGACY_INIT'` branch updates.
2. Before the first MERGE of a RUN, `destination.decision == "OK"`. Otherwise RUN raises and nothing is written.
3. Every non-null init `destination_id` matches `^\[("…")(,"…")*\]$` or is exactly `[]`. The literal `$[0]` no longer appears in `lgpmain`.
4. A `destination_id` comes from all mapped langs of one `poi_id` and only when they agree. Agreement is checked on the canonical string, and NULL against non-NULL counts as disagreement.
5. Multi-lang `poi_name` for `(poi_id, lang)` equals `poi_master.poi_name` of a legacy row whose `lang = lang`, or is NULL. It never comes from the `vi` row of another lang.
6. `NB_GLD_SRV_POI_MULTI_LANG` never reads `poi_name` from a source. P1 and P2 emit a STRING-typed NULL. `ML_COLS` does not contain `poi_name`.
7. `p_target_ws` is non-empty, matches `[A-Za-z][A-Za-z0-9_]*`, is not the old workspace, and equals the running workspace. Every write FQ starts with `TARGET_WS + "."`.
8. A rerun with the same pin inserts 0 rows into the map, info, and multi-lang tables, and changes no `poi_id`.
9. Pipeline `row_hash` values do not change when `poi_name` is added. `_hash_expr` uses `to_json(struct)`, and Spark `to_json` drops null fields, so there is no mass rewrite.
10. The gold `TABLE_SPECS` column set equals the `apps.srv_poi_multi_lang` columns minus `ingestion_ts`, which equals the entity columns minus `ingestion_ts`.

## State ownership

| State | Owner | Writers |
|---|---|---|
| `gld_srv_poi_info.destination_id`, rows with `load_origin = 'LEGACY_INIT'` | init | `NB_SETUP_LEGACY_GOLD_POI` stage `info` (upsert) |
| `gld_srv_poi_info.destination_id`, rows with `load_origin` NULL | pipeline | `NB_GLD_SRV_POI_INFO` (unchanged) |
| `gld_srv_poi_multi_lang.poi_name`, LEGACY_INIT rows | init | stage `multi_lang` (upsert) |
| `gld_srv_poi_multi_lang.poi_name`, pipeline rows | pipeline | `NB_GLD_SRV_POI_MULTI_LANG` writes NULL (D-02) |
| Ownership handover | pipeline | `sql_merge_target` with `owner_col`: on MATCHED it always updates, sets `load_origin = NULL`, and overwrites `poi_name` with NULL (D-02, accepted) |
| Gold schema `poi_name` | DDL | `init_tables` (fresh workspace), `lgpnamepy` (existing table), or `ensure_target` (fallback; column lands at the end) |
| `apps.srv_poi_multi_lang.poi_name` | PostgreSQL DDL | `gld_srv_serve.pg.sql` or a manual `ALTER` |

## Grain and keys

Unchanged. See `model-design.md` `## Entities and grain` and `## Keys`:

- `gld_srv_poi_info`: `poi_id`.
- `gld_srv_poi_multi_lang`: `(poi_id, lang)`.
- `poi_id` comes from `new_poi_id`.

New aggregation keys inside init:

- `dest_one`: unique per `poi_id`, built by `single_payload` over accepted rows.
- `name_one`: unique per `(poi_id, lang)`, built by `groupBy`.

Both are left-joined onto sources that are already unique on the same key, so a join cannot add rows. The existing `info_src.count() != n_before` guard and the `write_insert_only` duplicate-key guard still apply.

## Ordering

Inside `lgpmain`:

1. Preflight:
   - workspace guard;
   - load_origin types;
   - new: `ML_FQ.poi_name` is a string;
   - map columns;
   - pins;
   - new: `poi_master.destination_ids` is a string.
2. Map stage: `map_src`, drift, and `map_rows`.
3. New: the destination block. It computes `summary["destination"]`. In RUN, it raises when `decision != "OK"`.
4. The map write.
5. Info stage. `master_rows` no longer carries `destination_id`. `dest_one` is joined before `n_before`.
6. The multi_lang stage gains `name_one`.
7. Review, media, and amenity stages, unchanged.

Rollout order: PostgreSQL column, then gold column, then code deploy, then init PLAN, then init RUN. See Rollout.

## Transaction and commit boundaries

- Each stage commits through one Delta MERGE, which is atomic per table, with `userMetadata` `LEGACY_INIT:{EXEC}`. There is no cross-table transaction.
- The destination stop runs before any commit, so a shape or conflict stop leaves every table untouched.
- `lgpnamepy` makes one `ALTER` commit. It is a no-op when the column is already a string.
- PostgreSQL: one `ALTER TABLE ... ADD COLUMN`, which is transactional in PostgreSQL.

## Idempotency

- The map is insert-only and drift-guarded. Info and multi-lang use `legacy_upsert_sql`: insert new keys and overwrite LEGACY_INIT rows with values that are deterministic for a given pin. So a rerun converges, and the Dev repair is simply a RUN of the fixed notebook.
- Known side effect, accepted from the base task: every LEGACY_INIT row's `updated_at` is set to `batch_ts` on each RUN, even when its values did not change.
- `lgpnamepy` and the edited `legacyidpy` are no-ops on rerun.
- The PostgreSQL `ALTER` is manual. Rerunning it fails with "already exists" and changes nothing.

## Concurrency

- Init RUN holds `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` through `acquire_flow_lock` and `refresh_flow_lock` before each write. That is the same lock the 30M pipeline uses, so the init MERGE and the pipeline MERGE on `gld_srv_poi_multi_lang` never interleave.
- Invariant 7 (`TARGET_WS` equals the running workspace) guarantees the lock table and the target tables are in the same workspace.
- `lgpnamepy` holds the same lock (pattern copied from `legacyidpy`).
- PLAN mode takes no lock and only reads.

## Retry and recovery

- A failure in any stage prints `summary` with `failed_stage` and releases the lock in `finally`. Rerun RUN with the same `p_pin_json`; committed stages are re-applied idempotently.
- If the lock is busy, rerun later.
- On a `USER_DECISION` stop, nothing was written. The user decides, and the decision is recorded before any code change.

## Partial failure

| Failure point | State | Recovery |
|---|---|---|
| Destination stop | No writes | User decision |
| Map committed, info fails | Map rows exist (insert-only, deterministic) | Rerun |
| Info committed, multi_lang fails | Destinations fixed; names not yet set | Rerun |
| `lgpnamepy` not run before init | Preflight raises `chưa có poi_name` | Run `lgpnamepy`, then rerun |
| Pipeline ran before `lgpnamepy` | `ensure_target` added `poi_name` at the end of the table; `lgpnamepy` is then a no-op | None needed. Column order is cosmetic and every write is by name |
| Service deployed before the PostgreSQL column | Hibernate (`ddl-auto: none`) selects `poi_name`, so the query fails | Add the column, or roll the service back. See Rollout step order |

## Observability

New `summary` keys (printed and returned by `notebook.exit`):

- `target_ws`.
- `destination`: `{shape: {class: n}, stop_n, conflict_n, stop_samples (≤5 legacy_poi_id), conflict_samples (≤5 poi_id), decision}`.
- `info.destination_filled_n`.
- `multi_lang`: `name_conflict_n`, `name_filled_n`.

Samples contain ids only, never destination values.

`lgpnamepy` prints `lgpname: +|= poi_name <fq>`. Pipeline warnings are unchanged.

## Security

- `p_target_ws` is validated by regex before it is interpolated into identifiers. Init refuses the old workspace as a target.
- PLAN stays the default mode, and the parameter defaults to empty, so a bare run fails closed.
- There are no secrets and no bulk data in logs.

## Rollout

The runbook comes from `run-author --kind runbook`; this section is its input. The user runs every step. The Prod workspace name is supplied by the user and is never guessed.

**Dev**

1. PostgreSQL: `ALTER TABLE apps.srv_poi_multi_lang ADD COLUMN poi_name text;`
2. Deploy the repo notebooks. Run `NB_CREATE_DDL` cell `lgpnamepy` once; it takes the flow lock.
3. Deploy the service build that contains the entity field. It must not go before step 1.
4. Run `NB_SETUP_LEGACY_GOLD_POI` with `p_mode=PLAN` and `p_target_ws=sgr_visitvn_dev`.
   - Pin: prefer the original init's `p_pin_json`, taken from its summary or log. Otherwise use the latest pin.
   - Gate: `map.drift_n = 0`, `destination.decision = OK`, `multi_lang.name_conflict_n` reported.
   - If `decision = USER_DECISION`: stop and give the user the shape counts and samples.
5. Run with `p_mode=RUN` and the same pin. This repairs the existing LEGACY_INIT rows.
6. Checks: see Verification, runtime.

**Prod**

1. Same PostgreSQL step. On a fresh database, the updated `gld_srv_serve.pg.sql` already has the column.
2. Gold schema:
   - Fresh workspace: run `NB_SETUP_INITIAL_DDL`, which creates `poi_name` after `lang`.
   - Existing tables: run `lgpnamepy` instead.
3. Run `legacyidpy`, which now resolves the running workspace, to create the map and `load_origin`.
4. Deploy the service.
5. Run PLAN, then RUN, with `p_target_ws=<Prod workspace name supplied by the user>`, keeping the pins from the PLAN summary.

## Rollback and forward recovery

- **Code:** revert the notebooks.
  - The gold `poi_name` column is nullable and stays.
  - The old pipeline code does not return `poi_name`; `ensure_target` warns and leaves the values alone.
  - Do not rerun the old init code, because it would write `$[0]` again.
- **Service:** roll back the service first, then optionally drop the PostgreSQL column.
- **Data:** do not `RESTORE` gold tables, because that would discard pipeline commits. Use forward recovery instead:
  - Fix the code, then rerun init; it overwrites only LEGACY_INIT rows.
  - For an exact revert of one table, MERGE from `VERSION AS OF <v_pre from summary>`, restricted to keys with `load_origin = 'LEGACY_INIT'` in both versions. The runbook documents this; it is not code in this task.

## Alternatives

| Choice | Selected | Rejected and why |
|---|---|---|
| Serializer | Spark `to_json(from_json(.., 'array<string>'))` after a Python shape check | Python `json.dumps`: could drift from the pipeline's `to_json` escaping. A Spark-only check: `from_json` turns numbers into strings, so it cannot reject non-string elements |
| Conflict scope | All mapped langs | `vi` only: misses the disagreement the request names, and gives no value when `vi` is missing |
| Conflict action | Stop the whole run (request) | Dropping the key: silently loses rows |
| Name conflict | NULL for that key and count it | Adding the name to the content payload drops the whole row, which shrinks existing coverage. Stopping the run blocks on a rare case |
| Where the check runs | Before the map write | In the info stage: would leave a committed map on a Prod first run |
| `poi_name` position | After `lang` | After `experience`: breaks `test_multi_lang_experience_rule` |
| DDL workspace | Running workspace in the `NB_CREATE_DDL` cells | Parameter cell: `NB_CREATE_DDL` has none, and DDL always applies where the notebook runs |
| Dev repair | Rerun the init | Separate repair notebook: duplicates the logic. Changing `legacy_upsert_sql` to compare `row_hash`: outside scope and alters every stage |

## Implementation plan

Main records these in `decision.md` before editing:

- D-05: the §A Q1–Q4 rules.
- D-06: the §A Q5–Q7 rules.
- D-07: `TARGET_WS`, the `DICT_FQ` workspace, `legacyidpy` resolving the running workspace, and the new `lgpnamepy`.
- D-08: the §B scope extension.

Code for the edit rows follows.

### C1 lgppure addition (append at end of cell)

```python
DEST_ACCEPT = ("NULL", "EMPTY", "STRINGS")


def destination_ids_shape(text):
    """Lớp shape của poi_master.destination_ids. Chỉ NULL / EMPTY / STRINGS được ghi; lớp khác dừng USER_DECISION."""
    import json as _json
    if text is None:
        return "NULL"
    try:
        doc = _json.loads(text)
    except (TypeError, ValueError, RecursionError):
        return "NOT_JSON"
    if not isinstance(doc, list):
        return "NOT_ARRAY"
    if not doc:
        return "EMPTY"
    if any(item is None for item in doc):
        return "NULL_ELEMENT"
    if not all(isinstance(item, str) for item in doc):
        return "NON_STRING_ELEMENT"
    return "STRINGS"
```

### C2 lgpparams and lgpconst

Add `p_target_ws = ""` to `lgpparams`. Replace the target lines of `lgpconst`:

```python
import re

OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo"
TARGET_WS = (p_target_ws or "").strip()
if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", TARGET_WS):
    raise RuntimeError("p_target_ws phải là tên workspace đích: chữ, số, _")
if TARGET_WS == OLD.split(".", 1)[0]:
    raise RuntimeError("p_target_ws không được là workspace gold cũ")
MAP_FQ = f"{TARGET_WS}.lh_vv_gold.dbo.gld_poi_legacy_id_map"
INFO_FQ = f"{TARGET_WS}.lh_vv_gold.dbo.gld_srv_poi_info"
ML_FQ = f"{TARGET_WS}.lh_vv_gold.dbo.gld_srv_poi_multi_lang"
REV_FQ = f"{TARGET_WS}.lh_vv_gold.dbo.gld_srv_poi_review"
AMENITY_FQ = f"{TARGET_WS}.lh_vv_gold.dbo.gld_srv_poi_amenity"
MEDIA_FQ = f"{TARGET_WS}.lh_vv_gold.dbo.gld_srv_poi_media_gallery"
DICT_FQ = f"{TARGET_WS}.lh_vv_silver.dbo.ref_dictionary_amenities"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
```

### C3 lgpmain preflight

- `write_insert_only`: change the guard to `if not fq.startswith(TARGET_WS + "."): raise RuntimeError(f"Đích không thuộc {TARGET_WS}: {fq}")`.
- Workspace guard: `if _workspace_name() != TARGET_WS: raise RuntimeError(f"Notebook phải mở ở workspace {TARGET_WS}")`.
- After the `load_origin` loop: `if table_columns(ML_FQ).get("poi_name") != "string": raise RuntimeError(f"{ML_FQ} chưa có poi_name string: chạy lgpnamepy của NB_CREATE_DDL trước")`.
- After `pm_pin`: `if dict(pm_pin.dtypes).get("destination_ids") != "string": raise RuntimeError("poi_master.destination_ids không phải string")`.
- `summary` adds `"target_ws": TARGET_WS`.

### C4 lgpmain destination block

Insert after the `if p_mode == "RUN" and drift_n:` raise and the `map_rows = ...` line, before `if p_mode == "RUN": written = write_insert_only(MAP_FQ, ...`:

```python
    stage = "destination"
    shape_udf = F.udf(destination_ids_shape, "string")
    lp = pm.select(F.col("poi_id").alias("_lp"), F.col("destination_ids").alias("_ids"))
    dest_rows = (map_rows.where("poi_id_status = 'OK'").select("legacy_poi_id", "poi_id")
                 .join(lp, F.col("legacy_poi_id") == F.col("_lp"))
                 .withColumn("_shape", shape_udf(F.col("_ids"))))
    accepted = F.col("_shape").isin(*DEST_ACCEPT)
    dest_rows = dest_rows.withColumn(
        "destination_id", F.when(accepted, F.to_json(F.from_json(F.col("_ids"), "array<string>"))))
    dest_ok, dest_conflict = single_payload(dest_rows.where(accepted), ["poi_id"], ["destination_id"])
    dest_one = dest_ok.select("poi_id", F.col("_p").getItem(0)["destination_id"].alias("destination_id"))
    shape_n = {r["_shape"]: int(r["n"]) for r in
               dest_rows.groupBy("_shape").agg(F.count(F.lit(1)).alias("n")).collect()}
    stop_n = sum(n for k, n in shape_n.items() if k not in DEST_ACCEPT)
    conflict_n = dest_conflict.count()
    summary["destination"] = {
        "shape": shape_n, "stop_n": stop_n, "conflict_n": conflict_n,
        "stop_samples": [r["legacy_poi_id"] for r in dest_rows.where(~accepted)
                         .select("legacy_poi_id").orderBy("legacy_poi_id").limit(5).collect()],
        "conflict_samples": [r["poi_id"] for r in dest_conflict.select("poi_id").orderBy("poi_id").limit(5).collect()],
        "decision": "USER_DECISION" if stop_n or conflict_n else "OK",
    }
    if p_mode == "RUN" and summary["destination"]["decision"] != "OK":
        raise RuntimeError(f"USER_DECISION destination_ids: stop_n={stop_n} conflict_n={conflict_n} shape={shape_n}")
    stage = "map"
```

### C5 lgpmain info stage

- Change `master_cols` to `["is_recommended", "destination_name"]`.
- In `master_rows`, delete the `F.get_json_object(pm["destination_ids"], "$[0]").alias("destination_id"),` line.
- After `info_src = info_src.join(master_one, "poi_id", "left")`, add `info_src = info_src.join(dest_one, "poi_id", "left")` and `summary["info"]["destination_filled_n"] = info_src.where("destination_id IS NOT NULL").count()`. Both go before `n_before = info_src.count()`.

### C6 lgpmain multi_lang stage

Replace the `joined = ...` line and the `picked` select. Add the name join after `ml_src = ml_ok.select(...)`:

```python
    names_src = pm.select(F.col("poi_id").alias("_lp"), F.col("poi_name").alias("_pm_name"))
    joined = (display.join(mp, display["poi_id"] == mp["legacy_poi_id"], "left")
              .join(names_src, display["poi_id"] == F.col("_lp"), "left"))
    # ... summary_ml_base unchanged ...
    picked = joined.where(mp["legacy_poi_id"].isNotNull() & display["lang"].isNotNull()).select(
        mp["poi_id"], mp["lang"], mp["source_name"], *[display[c] for c in ML_PAY],
        display["experiences"].alias("experience"), F.col("_pm_name").alias("poi_name"))
    ml_ok, ml_conflict = single_payload(picked, ["poi_id", "lang"], pay)
    ml_src = ml_ok.select("poi_id", "lang", *[F.col("_p").getItem(0)[c].alias(c) for c in pay])
    name_g = picked.groupBy("poi_id", "lang").agg(F.collect_set(F.struct("poi_name")).alias("_n"))
    name_one = name_g.select("poi_id", "lang",
                             F.when(F.size("_n") == 1, F.col("_n").getItem(0)["poi_name"]).alias("poi_name"))
    ml_src = ml_src.join(name_one, ["poi_id", "lang"], "left")
```

`pay` does not contain `poi_name`. `summary["multi_lang"]` adds `"name_conflict_n": name_g.where(F.size("_n") > 1).count()` and `"name_filled_n": ml_src.where("poi_name IS NOT NULL").count()`.

### C7 NB_CREATE_DDL legacyidpy and lgpnamepy

In `legacyidpy`, replace `WS = "sgr_visitvn_dev"` with:

```python
WS = (notebookutils.runtime.context.get("currentWorkspaceName") or "").strip()
if not WS:
    raise RuntimeError("Không đọc được currentWorkspaceName")
```

Append markdown `lgpnamemd`: "# [THÊM 25/11] 20261125-legacy-init-destination-and-poi-name — thêm `poi_name` STRING sau `lang` trên `gld_srv_poi_multi_lang` của workspace đang mở. Không ghi dòng. Chạy lại không đổi gì."

Then code cell `lgpnamepy`:

```python
# [THÊM 25/11] 20261125-legacy-init-destination-and-poi-name (D-01, D-07)
# Thêm poi_name STRING NULL ngay sau lang trên gld_srv_poi_multi_lang của workspace đang mở.
# Chỉ đổi schema: không ghi dòng, không đổi cạnh / registry. Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M.
import uuid

WS = (notebookutils.runtime.context.get("currentWorkspaceName") or "").strip()
if not WS:
    raise RuntimeError("Không đọc được currentWorkspaceName")
WM = f"{WS}.lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
ML_FQ = f"{WS}.lh_vv_gold.dbo.gld_srv_poi_multi_lang"
NEW_COL = ("poi_name", "STRING")
ANCHOR = "lang"
LOCK = "lgpname-" + uuid.uuid4().hex


def _fields(fq):
    return {f.name.lower(): f.dataType.simpleString() for f in spark.table(fq).schema.fields}


def _exists(fq):
    try:
        spark.table(fq).schema
        return True
    except Exception:
        return False


n_lock = spark.sql(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{WID}'").first()["n"]
if n_lock != 1:
    raise RuntimeError(f"{WM} không có đúng 1 dòng {WID}: chạy plcadpy trước")
held = False
failed = None
try:
    spark.sql(f"""
    UPDATE {WM}
    SET lock_exec_id = '{LOCK}', lock_at = current_timestamp(), status = 'RUNNING', updated_at = current_timestamp()
    WHERE watermark_id = '{WID}' AND (
        lock_exec_id IS NULL
        OR coalesce(lock_at < current_timestamp() - INTERVAL {LEASE_MINUTES} MINUTES, true))
    """)
    held = True
    owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
    if not owner or owner["lock_exec_id"] != LOCK:
        held = False
        other = None if owner is None else owner["lock_exec_id"]
        raise RuntimeError(f"Luồng {PL} đang giữ khoá ({other}): chạy lại sau")

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    if not _exists(ML_FQ):
        raise RuntimeError(f"Dừng trước khi ghi: {ML_FQ} chưa có")
    fields = _fields(ML_FQ)
    if ANCHOR not in fields:
        raise RuntimeError(f"Dừng trước khi ghi: {ML_FQ} thiếu {ANCHOR}")
    if NEW_COL[0] in fields and fields[NEW_COL[0]] != "string":
        raise RuntimeError(f"Dừng trước khi ghi: {ML_FQ}.{NEW_COL[0]}={fields[NEW_COL[0]]}")

    def _refresh_lock():
        spark.sql(f"""
        UPDATE {WM}
        SET lock_at = current_timestamp(), updated_at = current_timestamp()
        WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
        """)
        owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
        if not owner or owner["lock_exec_id"] != LOCK:
            raise RuntimeError(f"Luồng {PL} mất khoá trước khi ghi")

    added = False
    if NEW_COL[0] not in fields:
        _refresh_lock()
        spark.sql(f"ALTER TABLE {ML_FQ} ADD COLUMNS (`{NEW_COL[0]}` {NEW_COL[1]} AFTER `{ANCHOR}`)")
        added = True

    # Sau khi ghi: chỉ xét cột cell thêm.
    if _fields(ML_FQ).get(NEW_COL[0]) != "string":
        raise RuntimeError(f"Sau khi ghi: {ML_FQ} chưa có poi_name string")
    print(f"lgpname: {'+' if added else '='} poi_name {ML_FQ}")
except Exception as exc:
    failed = exc
    raise
finally:
    if held:
        status = "FAILED" if failed else "SUCCESS"
        detail = "" if failed is None else str(failed).replace("'", " ")[:500]
        try:
            spark.sql(f"""
            UPDATE {WM}
            SET lock_exec_id = NULL, lock_at = NULL, status = '{status}', error_message = '{detail}',
                updated_at = current_timestamp()
            WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
            """)
        except Exception as cleanup_exc:
            if failed is None:
                raise
            raise failed from cleanup_exc
```

### C8 NB_GLD_SRV_POI_MULTI_LANG srvmlbuild

- Set `OUT_COLS = ("poi_id", "lang", "poi_name", "source_name", "time_to_spend", "best_time", "cost", "description", "experience")`. `ML_COLS` is unchanged.
- P1: keep the line `p1 = (rows.withColumn("description", description).withColumn("experience", experience)` exactly. Change the next line to `.withColumn("poi_name", F.lit(None).cast("string")).select(*OUT_COLS))`.
- P2: change the first select line to `p2 = (only.select(F.col("_pid").alias("poi_id"), F.col("_loc").alias("lang"), F.lit(None).alias("poi_name"),`. Keep the next two lines (`F.lit(PARTNER).alias("source_name"), ...` and `F.col("bio").alias("description"), ...`) and the cast-select line exactly; the cast gives `poi_name` the P1 type STRING.
- In `srvmlmd`, add one line: "`poi_name` = NULL trên P1 và P2 (nguồn chưa có cột). MERGE ghi đè `poi_name` của dòng LEGACY_INIT bằng NULL khi nhận dòng (D-02)."

### C9 PostgreSQL, entity, and docs

- `gld_srv_serve.pg.sql`:
  - After line 23, add the comment `-- DB đã có bảng trước 20261125-legacy-init-destination-and-poi-name: chạy tay ALTER TABLE apps.srv_poi_multi_lang ADD COLUMN poi_name text;`. The line must start with `--`, because a test forbids lines that start with `ALTER`.
  - In `CREATE TABLE apps.srv_poi_multi_lang`, add `    poi_name text,` after `    lang text NOT NULL,`.
- Entity: after the `lang` field, add `@Column(name = "poi_name")` and `private String poiName;`. Do not edit DTOs or `PoiService`.
- `mapping_gld_srv_poi_multi_lang.md`:
  - §1.1: add a bullet: `poi_name` is NULL on P1 and P2, there is no source column, LEGACY_INIT rows get the per-lang name from the init, and the MERGE that takes over a row overwrites it with NULL (D-02).
  - §1.2: insert this row right after the `lang` row: `| P1: không đọc<br>P2: không đọc | string | P1: null (slv_enr_poi_info_multi_lang chưa có poi_name)<br>P2: null | poi_name |`.
- `mapping_legacy_gold_to_gld_srv.md`:
  - Line 3: the target becomes `<p_target_ws>.lh_vv_gold.dbo`.
  - §1 row 7: "Cả JSON array, `to_json(from_json(.., array<string>))`, mọi lang của `poi_id` mới phải giống nhau; shape khác hoặc lệch thì dừng USER_DECISION".
  - §2 gets 14 columns, with `poi_name` from `poi_master.poi_name` of the legacy row of that lang, and a NULL on conflict.

### C10 Tests

`tests/test_srv_poi_serving_contract.py`:

- `test_destination_name_patch_cell`: change `ids[-8:]` to `ids[-10:]` and append `"lgpnamemd", "lgpnamepy"` to the list. Then `ids = ids[:-10]`.
- New `test_multi_lang_poi_name_across_layers`:
  - In `TABLE_SPECS`, `gld_srv_poi_multi_lang` names have `lang` followed by `poi_name`, and the type is `STRING`.
  - `OUT_COLS[2] == "poi_name"`, and `"poi_name" not in ML_COLS`.
  - `srvmlbuild` contains `.withColumn("poi_name", F.lit(None).cast("string"))` and `F.lit(None).alias("poi_name")`.
  - The PostgreSQL body contains `"    lang text NOT NULL,\n    poi_name text,\n"`, and the PostgreSQL text contains `ADD COLUMN poi_name text`.
  - When the service tree is present, the entity has `@Column(name = "lang")` before `@Column(name = "poi_name")`, and `SrvPoiMultiLang::getPoiName` does not appear under `src/main/.../service` or `api`.

`tests/test_legacy_gold_poi_init_contract.py`:

- `test_destination_ids_shape_classes`: exec `_func(lgppure, "destination_ids_shape")`. Expected classes:
  - `None` gives `NULL`.
  - `""` and `"abc"` give `NOT_JSON`.
  - `'{"a":1}'` and `'"x"'` give `NOT_ARRAY`.
  - `"[]"` gives `EMPTY`.
  - `'["a","b"]'` and `' ["a"] '` give `STRINGS`.
  - `'["a",null]'` gives `NULL_ELEMENT`.
  - `"[1]"` and `'[["a"]]'` give `NON_STRING_ELEMENT`.
  - Also assert `DEST_ACCEPT == ("NULL", "EMPTY", "STRINGS")` (literal in `lgppure`).
- `test_init_destination_full_array_before_writes`, on `lgpmain`:
  - `"$[0]"` does not appear.
  - The cell contains `F.to_json(F.from_json(F.col("_ids"), "array<string>"))` and `USER_DECISION destination_ids`.
  - `index("USER_DECISION destination_ids") < index("write_insert_only(MAP_FQ")`.
  - `master_cols = ["is_recommended", "destination_name"]` is present.
  - `info_src.join(dest_one, "poi_id", "left")` appears before `n_before = info_src.count()`.
- `test_init_target_workspace_param` replaces `test_init_write_targets_dev_only` and keeps its other assertions:
  - `lgpparams` has `p_target_ws = ""`.
  - `lgpconst` has no `sgr_visitvn_dev` and keeps `OLD` unchanged.
  - For each of `MAP_FQ`, `INFO_FQ`, `ML_FQ`, `REV_FQ`, `AMENITY_FQ`, `MEDIA_FQ`, `DICT_FQ`, the constant starts with `f"{TARGET_WS}.`.
  - `lgpmain` contains `_workspace_name() != TARGET_WS` and `fq.startswith(TARGET_WS + ".")`, and has no `sgr_visitvn_dev`.
- `test_legacy_upsert_updates_only_legacy_rows`, line 108: expect `MEDIA_FQ = f"{TARGET_WS}.lh_vv_gold.dbo.gld_srv_poi_media_gallery"`.
- `test_init_ml_poi_name_per_lang`, on `lgpmain`:
  - It contains `F.col("_pm_name").alias("poi_name")`, `name_g = picked.groupBy("poi_id", "lang")`, and `name_conflict_n`.
  - It contains `'chạy lgpnamepy của NB_CREATE_DDL trước'`.
  - `pay = ["source_name", *ML_PAY, "experience"]` is unchanged.
- `test_legacyid_ddl_cell_contract`: replace the `WS = "sgr_visitvn_dev"` assertion with `currentWorkspaceName` in the source and `sgr_visitvn_dev` not in the source.
- `test_poi_name_ddl_cell_contract`, on `lgpnamepy`:
  - `NEW_COL == ("poi_name", "STRING")` and `ANCHOR == "lang"`.
  - Token order: `held = True` < `Dừng trước khi ghi` < `_refresh_lock()` < `ADD COLUMNS` < `Sau khi ghi` < `finally:`.
  - Code lines contain no `DROP`, `DELETE`, `TRUNCATE`, `INSERT`, `UPDATE {CFG}`, or `sgr_visitvn_dev`.
  - Exactly one `ADD COLUMNS`, plus `" AFTER "`, `LEASE_MINUTES = 90`, `lock_exec_id = '{LOCK}'`, and `raise failed from cleanup_exc`.

## Verification

**Local, run by Main**

1. `python -m pytest tests/test_legacy_gold_poi_init_contract.py tests/test_srv_poi_serving_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py -q`
2. `python -m pytest -q`
3. `cd services/data-serving-service; .\mvnw.cmd -q -Dtest=PoiServiceTest test` (compile and unit only). Testcontainers integration tests need Docker; record them as not run.
4. `python scripts/vv.py verify 20261125-legacy-init-destination-and-poi-name`

Tests that must keep passing unchanged: `test_build_columns_match_ddl`, `test_multi_lang_experience_rule`, `test_multi_lang_i18n_only_branch`, `test_multi_lang_mapping_targets`, `test_node_specs`, `test_gold_and_pg_columns_and_types_match`, `test_entities_match_gold_columns_types_and_keys`, and `test_columns_match_sources`.

**Runtime checks, user-run through the runbook (counts only)**

- (a) LEGACY_INIT `destination_id` shapes, with the regexes from the probe: `bad = 0` and `json_array_null_elem = 0`. Also `count(destination_id NOT LIKE '[%' AND destination_id IS NOT NULL) = 0`.
- (b) Join multi-lang LEGACY_INIT rows to map and `poi_master` on `(poi_id, lang)` and compare names. `mismatch_n` must be 0 after excluding `name_conflict_n` keys. Also `count(lang <> 'vi' AND poi_name IS NOT NULL AND poi_name = <vi name of same legacy group> AND old lang name <> vi name) = 0`.
- (c) A second RUN with the same pin inserts 0 rows in map, info, and multi_lang. `count(*)` and `count(DISTINCT poi_id)` are unchanged.
- (d) Rows with `load_origin IS NULL` are identical between `v_pre` and `v_post` of info and multi_lang (`EXCEPT` count 0).
- (e) After one pipeline run, LEGACY_INIT rows taken over have `poi_name` NULL (D-02 is expected). Report that count.
