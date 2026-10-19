RESULT: PASS

## Main brief

### Decision
- Seed `amenity_raw` becomes key-only through `amenity_keys(raw)` in the shared `BEGIN_AMENITY_SEED` block. `SEED_ROWS` is a literal of 158 rows (84 google, 74 partner). `mapping_amenities.md` is not edited; the test derives the expected seed from it.
- The matcher classifies rows with pinned allowlists `FLAG_MATCH` (27 keys) and `TYPE_MATCH` (14 keys), keyed by `(business_sector, amenity_group, amenity_raw)`. Flag keys match `source_flags_json` = `true`. Type keys match exactly one element of `slv_poi_entity_non_enrich.types_json` (the existing `entity` input; no new edge). Every other row is skipped, as today.
- Duplicate gate: `validate_seed` fails on any 4-column duplicate except the pinned `AMENITY_SHARED_RAW` (the `goodForChildren` pair under attraction, unchanged and not a match key). The matcher fails on any duplicate condition.
- No DDL, column, grain, key-definition, or edge change. The rebuild is a user-run DEV runbook: DELETE plus setup reseed, DRY_RUN, DELETE plus forced RUN, with RESTORE/backup as the way back. No `DROP`.

### Invariants Main must preserve
- `SEED_ROWS == expand(parse_mapping(md), amenity_keys)`: 158 rows; google 84 (acc 31, f_n_b 34, attraction 16, shopping 3); partner 74, unchanged.
- Every seed raw is a fixed point: `amenity_keys(raw) == [raw]`. No seed value matches `^…(\.…)? = true$` or `^types\[\] = .+$`.
- Split rows copy source, sector, group, amenity, and amenity_vi from their source row. 117 source rows are unchanged character-for-character.
- 5-column dictionary key unique. 4-column duplicates are exactly `AMENITY_SHARED_RAW`, n=2.
- `FLAG_MATCH` (27) and `TYPE_MATCH` (14) are disjoint, neither contains the shared key, and both are subsets of the seed google keys. Every flag key resolves through `FLAG_KEYS`/`OBJECT_KEYS`.
- A row outside both allowlists, including the legacy ` = true` and `types[] = ` rows, never produces output.
- A code/dictionary mismatch (in either direction) leaves zero conditions → `QualityGateError` → no write.
- Type facts are deduplicated per `(poi_id, element)`. `SPEC` (inputs, pk, write_mode) is unchanged.
- The seed MERGE stays insert-only. The edge code and the edge count are unchanged.
- The two seed marker blocks are byte-identical.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupseed` header of `BEGIN_AMENITY_SEED` | add `import re`, `AMENITY_FLAG_RE`, `AMENITY_TYPES_RE`, `AMENITY_SHARED_RAW`, `amenity_keys` (doc §18 E1) | `test_amenity_keys_cases` passes |
| 2 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupseed` `SEED_ROWS` | regenerate the literal by applying `amenity_keys` in order (27 strips, 8→14 splits; doc §18 E2) | `test_seed_matches_mapping_file`, `test_seed_counts`, `test_seed_census` pass |
| 3 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupseed` `validate_seed` | replace with the 4-column duplicate rule plus the shared exception and the legacy-form check (doc §18 E1) | `test_seed_raw_unique_within_group` passes |
| 4 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_amenity` marker block | paste rows 1–3 identically; keep the tail `validate_seed(SEED_ROWS)` / `AMENITY_ROWS = list(SEED_ROWS)` | the `test_initial_ddl_contract.py` marker test passes |
| 5 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupplan` | add `STALE_SQL`, `stale_keys` in the print line and the PLAN exit (doc §18 E3) | `test_setup_contract` passes |
| 6 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupmerge` after `DRIFT` | `STALE = int(spark.sql(STALE_SQL).first()["n"])`, print it; the MERGE text is unchanged | `"WHEN MATCHED" not in merge` still holds |
| 7 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupexit` | add `"stale": STALE` to the summary | `test_setup_contract` passes |
| 8 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenmatch` `BEGIN_AMENITY_MATCH` | replace with doc §18 E4 (`TYPES_PATH`, `FLAG_MATCH`, `TYPE_MATCH`, `LEGACY_RE`, `resolve_condition(sector, group, raw)`, `is_legacy_form`, `match_conditions`) | `test_resolve_condition_cases`, `test_match_sets_pinned`, `test_match_conditions_states` pass |
| 9 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenbuild` `COND_SCHEMA`, `build` | replace with doc §18 E5; drop the `Counter` import; `SPEC` unchanged | `test_amenity_node_contract` passes |
| 10 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenmd` | new description (doc §18 E5, last paragraph) | text updated |
| 11 | tests/test_poi_amenity_contract.py | whole module | rewrite per doc §18 E7 table (oracles `FLAG_MATCH`/`TYPE_MATCH`, remove the local `resolve_condition`) | all listed tests exist and pass |
| 12 | tests/test_initial_ddl_contract.py | — | no edit expected; run only | passes unchanged |
| 13 | docs/context/01_DATA_MODEL.md | §6 table row N7; §6.1 row `ref_dictionary_amenities` | exact text in doc §18 E6 | 158/84/74 and the key-only rule are documented |
| 14 | docs/context/3p-google/mapping_amenities.md | — | no edit (doc §6 A2) | unchanged |

### Order and stop points
1. Rows 1–3, then run the seed tests.
2. Row 4, then run `tests/test_initial_ddl_contract.py`.
3. Rows 5–7.
4. Rows 8–10.
5. Row 11, then run the full suite.
6. Row 13.
7. **STOP A (evidence):** full pytest output for `local_verification`.
8. **STOP B (review):** sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer, risk-gate.
9. **STOP C (user):** after review PASS, the runbook author writes `runtime-runbook.md` from doc §19. The user runs it on DEV, with stops R1 (user decision on manual DEV rows, drift, edges), R2 (evidence: dictionary 158, edges unchanged), and R3 (user acceptance or rollback per doc §17). Agents never set `gates.runtime`.

### Tests and verification
- `python -m pytest tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest tests -q`
- New or changed tests in `tests/test_poi_amenity_contract.py`: `test_seed_matches_mapping_file`, `test_amenity_keys_cases`, `test_seed_census`, `test_seed_counts`, `test_seed_split_rows_keep_columns`, `test_seed_excludes_placeholders`, `test_seed_raw_unique_within_group`, `test_hoac_split_same_amenity`, `test_resolve_condition_cases`, `test_match_sets_pinned`, `test_legacy_form_consistent`, `test_match_conditions_states`, `test_flag_keys_match_registry`, `test_amenity_node_contract`, `test_setup_contract`, `test_seed_sectors_groups`, `test_seed_sectors_in_entity_vocabulary`.
- Runtime expectations (doc §15): `dict_google_active=84`, `conditions_matchable=41` (flag 27, type 14), `conditions_skipped=43`, `dict_legacy_form=0`; setup `inserted=158`, `stale=0`, `edges_inserted=0`, `edges_retired=0`.

### Read only if needed
- §5 Invariants, §6 A1/A3 (allowlist, duplicate-gate scope) → rows 3, 8, 11
- §6 A2 (seed representation) → rows 1, 2, 14
- §6 A4 (types from entity) → row 9
- §18 E1–E2 → rows 1–4
- §18 E3 → rows 5–7
- §18 E4–E5 → rows 8–10
- §18 E6 → row 13
- §18 E7 → rows 11–12
- §10–§14, §17, §19 (commits, idempotency, concurrency, rollback, runbook) → STOP C
- §21 residual risks → review notes

# Architecture: 20261019-amenity-raw-key-only

## 1. Design summary

- The seed `amenity_raw` becomes key-only through a pure function `amenity_keys(raw)` in the shared `BEGIN_AMENITY_SEED` block. `SEED_ROWS` holds the 158 rewritten rows as a literal. `docs/context/3p-google/mapping_amenities.md` stays as the business source. The contract test derives the expected seed from it with `amenity_keys`.
- After the rewrite, a bare key no longer shows where it came from. `outdoorSeating` from `outdoorSeating = true` looks the same as the unchanged bare `restroom` or `goodForChildren` under `attraction`, and the same as `dim_sum_restaurant` under `f_n_b`. The matcher therefore classifies dictionary rows with two pinned allowlists keyed by `(business_sector, amenity_group, amenity_raw)`: `FLAG_MATCH` (27 keys) and `TYPE_MATCH` (14 keys). Any row outside both lists keeps today's behavior: it is skipped.
- Flag keys match `source_flags_json` path = `true`. Type keys match exactly one element of `slv_poi_entity_non_enrich.types_json`. That table is already the `entity` input, so no new edge or input is added.
- The rebuild is a user-run DEV runbook after review PASS: baseline, backup, then STOP. Next, DELETE the dictionary under the flow lock and run `NB_SETUP_POI_AMENITY` with `p_apply=true`, then STOP. Next, DRY_RUN the node, DELETE `slv_poi_amenity` under the lock, and RUN the node with `p_force=true`, then STOP. No `DROP`. The way back is `RESTORE TABLE ... TO VERSION AS OF`, with CTAS backups as the fallback.

## 2. Scope

- `notebooks/NB_SETUP_POI_AMENITY.ipynb`: seed block `c1setupseed`; read-only stale-key count in `c1setupplan`, `c1setupmerge`, `c1setupexit`.
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb`: `init_seed_amenity`, a byte-identical copy of the seed block. The cell tail `validate_seed(SEED_ROWS)` / `AMENITY_ROWS = list(SEED_ROWS)` stays unchanged.
- `notebooks/NB_SLV_POI_AMENITY.ipynb`: `d1amenmd`, `d1amenmatch` (`BEGIN_AMENITY_MATCH`), `d1amenbuild`.
- `tests/test_poi_amenity_contract.py`: rewritten seed, matcher, and transition tests.
- `tests/test_initial_ddl_contract.py`: no edit expected. Its marker-equality test (`init_seed_amenity` == `c1setupseed`) is the guard. Edit it only if that test needs a token for the new names.
- `docs/context/01_DATA_MODEL.md`: §6 row N7 and §6.1 row `ref_dictionary_amenities`.
- `docs/context/3p-google/mapping_amenities.md`: no edit (see A2).
- Runbook design (§19). `runtime-runbook.md` is written after review PASS by the runbook author, not by this design.

## 3. Non-goals

- No DDL change, no new column (`match_kind` is rejected in A1), no grain or key-definition change.
- No new pipeline edge, input, or entity input name. Inputs stay `slv_3p_poi_amenity`, `slv_poi_entity_non_enrich`, `ref_dictionary_amenities`.
- No rewrite of narrative `types[] có ...` / `types[] thuộc ...` text, bare tokens, comma lists, `serves_meals = true`, or `outdoorSeating = true = true`.
- No change to partner rows and no partner matching.
- No change to seed MERGE semantics. The MERGE stays `WHEN NOT MATCHED THEN INSERT` only.
- The agent does not set `gates.runtime` and does not run anything on Fabric.
- No removal of the pre-existing duplicate `('google','attraction','facilities_and_services','goodForChildren')` (see A3).

## 4. Model source

- `model-design.md` does not exist. This task does not need it. Table set, columns, grain, and key definitions stay exactly as in `docs/context/01_DATA_MODEL.md` §6 N7 (grain `(poi_id, business_sector, amenity_group, amenity_raw)`) and §6.1 (dictionary key `(source_name, business_sector, amenity_group, amenity_raw, amenity)`), confirmed by ledger D4. Only the key values, seed cardinality, and the matching rule change. One column-level lineage is added: `slv_poi_entity_non_enrich.types_json` → `slv_poi_amenity`, through an input that already exists. If a reviewer treats that lineage as a model change, the blocking step is `python scripts/vv.py run-author 20261019-amenity-raw-key-only --kind model`.

## 5. Invariants

- I1. The seed has 158 rows: 74 partner and 84 google. By sector, google is accommodation 31, f_n_b 34, attraction 16, shopping_n_retail 3. Partner per-sector counts are unchanged (22/18/22/12).
- I2. `SEED_ROWS` == `[(s, sec, g, k, en, vi) for (s, sec, g, raw, en, vi) in parse_mapping(md) for k in amenity_keys(raw)]`. The order is mapping order, with split keys in written order.
- I3. Each seed `amenity_raw` is a fixed point: `amenity_keys(raw) == [raw]`. No seed value has the flag form `^[A-Za-z][A-Za-z0-9]*(\.[A-Za-z][A-Za-z0-9]*)? = true$` or the form `^types\[\] = .+$`.
- I4. 117 source rows are unchanged character-for-character. That includes all partner rows. 27 flag rows lose ` = true`. 8 `types[] = ...` rows become 14 rows, and every split row keeps `source_name`, `business_sector`, `amenity_group`, `amenity`, `amenity_vi`.
- I5. The dictionary 5-column key is unique. The 4-column key `(source_name, business_sector, amenity_group, amenity_raw)` is unique, except for the keys in `AMENITY_SHARED_RAW`, which is exactly `{('google','attraction','facilities_and_services','goodForChildren')}`. Any other 4-column duplicate fails `validate_seed`.
- I6. Matcher conditions are unique on `(business_sector, amenity_group, amenity_raw)`. A duplicate raises `QualityGateError` before any write. The lib exit check `pk_duplicate` stays as a backstop.
- I7. `FLAG_MATCH` has 27 keys and `TYPE_MATCH` has 14. The two are disjoint and neither contains `AMENITY_SHARED_RAW`. Both are subsets of the seed's google 4-column keys. Every `FLAG_MATCH` key resolves to a `source_flags_json` path through `FLAG_KEYS` / `OBJECT_KEYS`.
- I8. A dictionary row outside `FLAG_MATCH ∪ TYPE_MATCH` never produces a `slv_poi_amenity` row. That includes legacy-form rows left by an insert-only rerun.
- I9. When the code and dictionary versions do not match (new code with old dictionary, or old code with new dictionary), the matcher finds zero conditions. It raises `QualityGateError` and writes nothing. It does not soft-delete the existing rows.
- I10. `ctrl_mng_pipeline_config` edges into `slv_poi_amenity` for `PL_VV_TRANS_SLV_TO_SLV_1H` are unchanged by code and by the runbook: 3 active UPSERT edges, the `slv_poi_entity` edge not active, and at most one row per `(pl, src_schema, src_tbl, trg_schema, trg_tbl)` (D5).
- I11. The runbook never runs `DROP TABLE` on either table. Every destructive step (DELETE) comes after a recorded baseline version, a verified backup, and a user stop.

## 6. Alternatives and trade-offs

### A1. Telling flag, type, and unchanged keys apart in the matcher

| Option | Effect | Verdict |
|---|---|---|
| (a) Pinned allowlists `FLAG_MATCH` / `TYPE_MATCH` keyed by `(sector, group, raw)` in `BEGIN_AMENITY_MATCH`, tied to the seed by tests | Meets the request exactly, including "unchanged rows keep current behavior". No schema change. Fails closed. | **Selected** |
| (b) New column `match_kind` in `ref_dictionary_amenities` | Rules stay as data. But it changes a table and its DDL in two notebooks, needs `model-design.md`, and goes beyond the request. | Rejected for this task; backlog candidate |
| (c) Classify by value form only (flag if it resolves to a flags path, type if snake_case) | 9 unchanged google rows (attraction bare flag names, `delivery`, `paymentOptions.acceptsCreditCards`) and about 16 bare type tokens would start matching. The two `goodForChildren` rows under attraction would produce duplicate output primary keys. That breaks the request rule and I6. | Rejected |

Trade-off accepted: a steward who adds a new key-form google row to the dictionary gets no match until the code allowlist changes. Today any `x = true` row with a known head matches without a code change. The run metric `conditions_skipped` makes this visible. Recorded as a residual risk (§21).

### A2. Seed representation

| Option | Verdict |
|---|---|
| (a) `SEED_ROWS` literal in the new form (158 rows) plus `amenity_keys` in the block. The md stays unchanged, and the test bridges md → seed | **Selected.** What lands in the table is reviewable as is. The business mapping keeps its original wording. |
| (b) Edit `mapping_amenities.md` to the key-only form | Rejected. The doc would lose the difference between flag-derived and bare rows. Splitting needs either duplicated md rows (which duplicates partner rows) or abusing `hoặc`. |
| (c) Keep the 152-row source literal and expand it at runtime | Rejected. The literal would not equal the table content, and the shared marker block would carry logic, not data. |

### A3. Scope of the duplicate-key gate

The acceptance criterion says two equal keys in the same `(source_name, business_sector, amenity_group)` fail the quality gate. The mandated 158-row seed already has one such pair: `goodForChildren` under attraction, amenities `Good for Children` and `Family Friendly`. Both rows are unchanged bare tokens and are not match keys. A gate over every row would make the required seed impossible to write. Selected: (1) `validate_seed` fails on any 4-column duplicate outside the pinned `AMENITY_SHARED_RAW` exception. That covers any duplicate a split or flag strip could create, and any new duplicate. (2) The matcher fails on any duplicate among match conditions, with no exception. Only conditions can collide on the output primary key. Rejected: deleting or renaming one of the two rows. That changes seed content outside the two form rules and needs a user decision.

### A4. Source of `types`

| Option | Verdict |
|---|---|
| (a) `slv_poi_entity_non_enrich.types_json` (existing `entity` input, grain `poi_id`, google rows only, `array<string>` JSON as already parsed by `NB_SLV_POI_ENTITY_NON_ENRICH`) | **Selected.** No new edge. Same snapshot as `business_sector`. |
| (b) New input `slv_3p_poi.types_json` | Rejected. It adds an edge (against D5 and the stated scope) and a second POI grain to reconcile. |

Matching is exact string equality between the key and one array element. No lowercasing: the request says "khớp đúng một phần tử", and Google type tokens are canonical. Type facts are deduplicated per `(poi_id, element)`, so a repeated element cannot duplicate the output primary key.

### A5. Rebuild method

| Option | Verdict |
|---|---|
| (a) DELETE dictionary → setup reseed → DRY_RUN → DELETE `slv_poi_amenity` → forced node RUN | **Selected.** This is "như init lần đầu": fresh `updated_at`/`created_at`, no soft-deleted history. Every step is idempotent and fails closed. |
| (b) Setup first (insert-only adds 41 keys), then DELETE only the stale rows | The dictionary is never empty, but this is not a full reload: `updated_at` and `is_active` of 117 rows are carried over. Kept as the fallback if the user rejects the empty window. |
| (c) Run the node only (MERGE soft-deletes old keys) | Leaves 35 legacy dictionary rows and soft-deleted amenity rows. Does not meet the request. |
| (d) DROP/CREATE | Forbidden by the request and I11. |

## 7. State ownership

| State | Owner (writer) | Readers |
|---|---|---|
| `lh_vv_silver.dbo.ref_dictionary_amenities` | `NB_SETUP_POI_AMENITY` / `NB_SETUP_INITIAL_DDL` (insert-only seed); the runbook (one DELETE, optional RESTORE) | `NB_SLV_POI_AMENITY` (`dict`) |
| `lh_vv_silver.dbo.slv_poi_amenity` | `NB_SLV_POI_AMENITY` via lib `run_node` MERGE; the runbook (one DELETE, optional RESTORE) | none in the ctrl seed |
| `ctrl_mng_pipeline_config` amenity edges | `NB_SETUP_POI_AMENITY` `_write_edges` (MERGE, existing) | NB_00, lib |
| Flow lock `PL_VV_TRANS_SLV_TO_SLV_1H` | lib `acquire_flow_lock` / `release_flow_lock` | setup, node, runbook DELETE cells |
| Match classification | Code: `FLAG_MATCH`, `TYPE_MATCH` in `NB_SLV_POI_AMENITY` | tests |
| Seed content | Code: `SEED_ROWS` in two identical blocks | tests, setup |

## 8. Grain and keys

- `ref_dictionary_amenities`: key unchanged (01_DATA_MODEL §6.1, D4). Cardinality goes from 152 to 158. The 4-column uniqueness of I5 is a seed rule, not a table key.
- `slv_poi_amenity`: grain unchanged `(poi_id, business_sector, amenity_group, amenity_raw)` (§6 N7, D4). Values become key-only. Type rows are new and come from `types_json`. One output row per (POI, matched condition). Two type keys of the same amenity (for example `bakery` and `pastry_shop`) give two rows with different `amenity_raw`, as flag pairs such as the two `Parking` rows already do.
- Entity grain `poi_id` (§6 N6) keeps the `entity` join 1:1.

## 9. Ordering

- Code: the seed block is edited first and copied to `NB_SETUP_INITIAL_DDL`, then the matcher, then the tests, then the docs. One commit or PR, so the seed and matcher reach DEV together.
- Runtime: code deploy → baseline/backup → dictionary DELETE → seed → dictionary checks → node DRY_RUN → amenity DELETE → node RUN → checks. The dictionary always comes before the amenity table, because the node reads the dictionary. Rollback order does not matter for safety (I9). Doing the dictionary first is recommended.
- Inside the node: build the conditions in Python (gate) → read the inputs → join → metrics → MERGE (lib).

## 10. Transaction and commit boundaries

- Node: one Delta MERGE commit on `slv_poi_amenity` per RUN (lib `merge_target`). The quality gates (`match_conditions` dup/empty, lib exit check) run before it. DRY_RUN does not commit.
- Setup: `validate_seed` runs in `c1setupplan` before any DDL or write. Then the seed MERGE commit (no flow lock, existing behavior), then the edge MERGE commit under the flow lock. These are two separate commits.
- Runbook: four data commits — DELETE dictionary, seed MERGE, DELETE amenity, node MERGE. Each is atomic on its own. Nothing spans tables. Between commits the state is either correct or fails closed (§13).

## 11. Idempotency

- `amenity_keys` is idempotent on its own output. `validate_seed` enforces this through I3.
- A setup rerun inserts 0 rows (`missing_before = 0`) and leaves the edges unchanged (`edges_inserted = 0`, `edges_retired = 0`).
- A node rerun on unchanged inputs: same `row_hash` → MERGE with diff 0.
- Runbook: DELETE on an empty table is a no-op, and every step can be repeated from the last stop. RESTORE to a fixed version is idempotent.
- Insert-only rerun without a rebuild: 35 legacy rows stay. The matcher skips them (I8) and reports `dict_legacy_form = 35`. Output stays correct, and the setup reports `stale_keys = 35`.

## 12. Concurrency

- The pipeline is not scheduled and runs manually (§6 N7). The runbook first checks that no trigger exists and that the lock row has no live `lock_exec_id`.
- Runbook DELETE cells take the flow lock with `acquire_flow_lock(PL, X, X, LOCK_TIMEOUT_DEFAULT_MIN)` and release it in `finally`. They do not hold the lock across the setup or node calls, because those take the same lock themselves (a manual RUN takes it; the setup takes it for edges).
- The seed MERGE runs outside the lock (existing). A node run that interleaves reads a Delta snapshot: either an empty dictionary (fails closed) or the full seed.
- Delta optimistic concurrency: a DELETE that conflicts with a MERGE fails one side, and that step is rerun.

## 13. Partial failure

| Failure point | Resulting state | Action |
|---|---|---|
| Backup CTAS fails or counts differ | Nothing deleted | Stop; fix; repeat the backup |
| After the dictionary DELETE, before the seed | Dictionary empty; node raises "không có key google khớp được"; amenity untouched | Run the setup again |
| `validate_seed` fails in the setup | No write (raised in the plan cell) | Code defect; stop; forward fix |
| Seed MERGE committed, edge precheck raises `ConfigError` | Dictionary correct; edges unchanged | STOP for a user decision on the ctrl edges; do not edit edges by hand |
| DRY_RUN raises the dup/empty QG | Nothing written | Stop; inspect the dictionary |
| After the amenity DELETE, node RUN fails | Amenity empty; no downstream edge reads it | Fix forward and rerun RUN, or roll back (§17) |
| Node MERGE interrupted | Atomic; the previous version stays | Rerun RUN |

## 14. Retry and recovery

- Notebook writes already use `with_retry` (seed, edges) and the lib's own retry around MERGE. No new retry code.
- Runbook steps are retried manually from the last passed STOP. Every step is idempotent (§11).
- Recovery prefers fixing forward. The data rollback (§17) is for a rejected outcome, not for transient errors.

## 15. Observability

- Setup PLAN exit (`p_apply=false`): `google`, `partner`, `missing_keys`, new `stale_keys` (rows in the table whose 5-column key is not in the seed), `entity_edges_ok`.
- Setup apply summary: `inserted`, `drift`, new `stale`, `edges_inserted`, `edges_retired`.
- Node `ctx.metrics`: the existing `src_rows`, `pois_joined`, `pois_without_entity`, `unparsed_json`, `dict_google_active`, `conditions_matchable`, `conditions_skipped`, `rows`, plus new `conditions_flag`, `conditions_type`, `dict_legacy_form`, `rows_flag`, `rows_type`.
- Expected after the rebuild: `dict_google_active = 84`, `conditions_matchable = 41`, `conditions_flag = 27`, `conditions_type = 14`, `conditions_skipped = 43`, `dict_legacy_form = 0`, `rows = rows_flag + rows_type`.
- The runbook records aggregates and Delta versions only.

## 16. Security

DEV only (`lh_vv_silver.dbo`, `lh_vv_ctrl.dbo`). No secrets, no new credentials or endpoints. Evidence holds aggregates and versions. Any `poi_id` sample is capped at 50 rows. Backup tables sit in the same lakehouse with the same access. Not applicable beyond that: no personal data is added to any table.

## 17. Rollout, rollback, and forward recovery

Rollout:
1. Code commit/PR (§18), local tests pass, reviews pass (sql-data, spark-runtime, state-correctness, risk-gate).
2. Sync the notebooks to the DEV workspace. Until the runbook reseeds, a node run fails closed (I9).
3. The user runs the runbook (§19). The agent does not set `gates.runtime`.

Rollback (the outcome is rejected at STOP R3, or later):
1. Under the flow lock: `RESTORE TABLE lh_vv_silver.dbo.ref_dictionary_amenities TO VERSION AS OF <V_dict0>`, then the same for `slv_poi_amenity` with `<V_amen0>`.
2. If RESTORE fails (files vacuumed): `DELETE FROM <t>` then `INSERT INTO <t> SELECT * FROM <bak_t>`, under the lock.
3. `git revert` the code commit and sync DEV. Either half alone fails closed (I9), so a code/data mismatch never writes wrong rows.
4. Verify the counts equal the baseline. Edges need no rollback (never changed).

Forward recovery: fix the defect, redeploy, rerun from the last passed STOP. A RESTOREd old dictionary with new code is also recovered forward by repeating R2 to R3.

## 18. Implementation plan

### E1. Shared seed block (`c1setupseed` and `init_seed_amenity`, between `# BEGIN_AMENITY_SEED` and `# END_AMENITY_SEED`)

Add at the top of the block. Keep `SEED_SECTORS`, `SEED_GROUPS`, `SEED_SKIP`. Replace `validate_seed`. Use the amenity prefix so names do not collide with the place-type cell in `NB_SETUP_INITIAL_DDL`.

```python
import re

AMENITY_FLAG_RE = re.compile(r"([A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z][A-Za-z0-9]*)?) = true")
AMENITY_TYPES_RE = re.compile(r"types\[\] = (.+)")
# Khoá 4 cột trùng có sẵn từ mapping, dạng giữ nguyên, không phải key khớp.
AMENITY_SHARED_RAW = (("google", "attraction", "facilities_and_services", "goodForChildren"),)


def amenity_keys(raw):
    """amenity_raw mapping -> list key. "a.b = true" -> ["a.b"]; "types[] = x, y" -> ["x", "y"]; dạng khác giữ nguyên."""
    flag = AMENITY_FLAG_RE.fullmatch(raw)
    if flag:
        return [flag.group(1)]
    types = AMENITY_TYPES_RE.fullmatch(raw)
    if types:
        return [part.strip() for part in types.group(1).split(",")]
    return [raw]
```

```python
def validate_seed(rows):
    """Seed phải đúng nguồn, sector, nhóm, khoá 5 cột, chỉ còn dạng key; khoá 4 cột trùng chỉ trong AMENITY_SHARED_RAW."""
    keys = [row[:5] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("ref_dictionary_amenities: trùng khoá 5 cột")
    counts = {}
    for row in rows:
        counts[row[:4]] = counts.get(row[:4], 0) + 1
    dup = sorted(key for key, n in counts.items() if n > 1 and key not in AMENITY_SHARED_RAW)
    if dup:
        raise ValueError(f"ref_dictionary_amenities: trùng amenity_raw trong (source, sector, group): {dup}")
    for source, sector, group, raw, amenity, _vi in rows:
        if source not in {"google", "partner"}:
            raise ValueError(f"source lạ: {source}")
        if sector not in SEED_SECTORS:
            raise ValueError(f"sector lạ: {sector}")
        if group not in SEED_GROUPS:
            raise ValueError(f"group lạ: {group}")
        if not raw or raw in SEED_SKIP:
            raise ValueError(f"amenity_raw không hợp lệ: {raw}")
        if amenity_keys(raw) != [raw]:
            raise ValueError(f"amenity_raw còn dạng cũ: {raw}")
        if not amenity:
            raise ValueError(f"amenity trống: {raw}")
```

Generate the `SEED_ROWS` literal by applying `amenity_keys` to the current 152 rows in order (E2), then paste the whole block unchanged into `init_seed_amenity`.

### E2. Seed value changes (35 source rows → 41 rows; all other columns copied)

Flag rows: remove ` = true` (27 rows). accommodation/general_amenities: `parkingOptions.freeStreetParking`, `parkingOptions.valetParking`, `parkingOptions.freeGarageParking`, `parkingOptions.paidGarageParking`, `outdoorSeating`, `restroom`, `goodForChildren`, `goodForGroups`, `liveMusic`, `parkingOptions.freeParkingLot`, `parkingOptions.paidParkingLot`, `servesCocktails`, `parkingOptions.freeElectricVehicleParking`, `parkingOptions.paidElectricVehicleParking`. accommodation/accessibility: `accessibilityOptions.wheelchairAccessible{Seating,Elevator,Entrance,Restroom,Parking}`. f_n_b/space_and_services: `restroom`, `goodForChildren`, `accessibilityOptions.wheelchairAccessibleEntrance`, `goodForWatchingSports`, `liveMusic`, `dineIn`. attraction/facilities_and_services: `parkingOptions.freeParkingLot`, `parkingOptions.paidParkingLot`.

Types rows (8 → 14):

| sector/group | old | new rows (amenity / amenity_vi unchanged) |
|---|---|---|
| accommodation/general_amenities | `types[] = swimming_pool` | `swimming_pool` |
| accommodation/general_amenities | `types[] = hot_spring, sauna` | `hot_spring`, `sauna` |
| accommodation/general_amenities | `types[] = garden, botanical_garden` | `garden`, `botanical_garden` |
| accommodation/general_amenities | `types[] = meeting_rooms` | `meeting_rooms` |
| f_n_b/specialty_tags | `types[] = food_stand, street_food_gathering` | `food_stand`, `street_food_gathering` |
| f_n_b/specialty_tags | `types[] = seafood_restaurant, oyster_bar_restaurant` | `seafood_restaurant`, `oyster_bar_restaurant` |
| f_n_b/specialty_tags | `types[] = steakhouse` | `steakhouse` |
| f_n_b/specialty_tags | `types[] = bakery, pastry_shop, cake_shop` | `bakery`, `pastry_shop`, `cake_shop` |

### E3. Setup stale-key count (`c1setupplan`, `c1setupmerge`, `c1setupexit`)

In `c1setupplan`, define this after `seed_df.createOrReplaceTempView("seed_amenities")`:

```python
STALE_SQL = f"""
    SELECT count(*) AS n
    FROM {REF_FQ} t
    LEFT ANTI JOIN seed_amenities s
      ON t.source_name = s.source_name
     AND t.business_sector = s.business_sector
     AND t.amenity_group = s.amenity_group
     AND t.amenity_raw = s.amenity_raw
     AND t.amenity = s.amenity
"""
```

Set `stale_keys = spark.sql(STALE_SQL).first()["n"]` in the `table_exists` branch, and `stale_keys = 0` otherwise. Add `stale_keys={stale_keys}` to the print line and `"stale_keys": int(stale_keys)` to the PLAN exit JSON. In `c1setupmerge`, after `DRIFT`, add `STALE = int(spark.sql(STALE_SQL).first()["n"])` and include it in the print. In `c1setupexit`, add `"stale": STALE` to the summary. Read-only; never a failure. The MERGE text stays unchanged (`test_setup_contract`).

### E4. Matcher block (`d1amenmatch`, full replacement between the markers)

```python
# BEGIN_AMENITY_MATCH
import re

FLAG_KEYS = ("servesBreakfast", "servesBrunch", "servesLunch", "servesDinner", "servesBeer", "servesWine",
             "servesCocktails", "servesDessert", "servesCoffee", "servesVegetarianFood", "allowsDogs",
             "goodForChildren", "goodForGroups", "goodForWatchingSports", "liveMusic", "menuForChildren",
             "outdoorSeating", "restroom", "reservable", "takeout", "delivery", "dineIn", "curbsidePickup")
OBJECT_KEYS = ("parkingOptions", "paymentOptions", "accessibilityOptions", "evChargeOptions", "fuelOptions")
TYPES_PATH = "types[]"
# Key cờ (seed "key = true" bỏ hậu tố): khớp source_flags_json = true. Khoá (business_sector, amenity_group, amenity_raw).
FLAG_MATCH = frozenset({
    ("accommodation", "general_amenities", "parkingOptions.freeStreetParking"),
    ("accommodation", "general_amenities", "parkingOptions.valetParking"),
    ("accommodation", "general_amenities", "parkingOptions.freeGarageParking"),
    ("accommodation", "general_amenities", "parkingOptions.paidGarageParking"),
    ("accommodation", "general_amenities", "outdoorSeating"),
    ("accommodation", "general_amenities", "restroom"),
    ("accommodation", "general_amenities", "goodForChildren"),
    ("accommodation", "general_amenities", "goodForGroups"),
    ("accommodation", "general_amenities", "liveMusic"),
    ("accommodation", "general_amenities", "parkingOptions.freeParkingLot"),
    ("accommodation", "general_amenities", "parkingOptions.paidParkingLot"),
    ("accommodation", "general_amenities", "servesCocktails"),
    ("accommodation", "general_amenities", "parkingOptions.freeElectricVehicleParking"),
    ("accommodation", "general_amenities", "parkingOptions.paidElectricVehicleParking"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleSeating"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleElevator"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleEntrance"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleRestroom"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleParking"),
    ("f_n_b", "space_and_services", "restroom"),
    ("f_n_b", "space_and_services", "goodForChildren"),
    ("f_n_b", "space_and_services", "accessibilityOptions.wheelchairAccessibleEntrance"),
    ("f_n_b", "space_and_services", "goodForWatchingSports"),
    ("f_n_b", "space_and_services", "liveMusic"),
    ("f_n_b", "space_and_services", "dineIn"),
    ("attraction", "facilities_and_services", "parkingOptions.freeParkingLot"),
    ("attraction", "facilities_and_services", "parkingOptions.paidParkingLot"),
})
# Key tách từ seed "types[] = a, b": khớp đúng một phần tử slv_poi_entity_non_enrich.types_json.
TYPE_MATCH = frozenset({
    ("accommodation", "general_amenities", "swimming_pool"),
    ("accommodation", "general_amenities", "hot_spring"),
    ("accommodation", "general_amenities", "sauna"),
    ("accommodation", "general_amenities", "garden"),
    ("accommodation", "general_amenities", "botanical_garden"),
    ("accommodation", "general_amenities", "meeting_rooms"),
    ("f_n_b", "specialty_tags", "food_stand"),
    ("f_n_b", "specialty_tags", "street_food_gathering"),
    ("f_n_b", "specialty_tags", "seafood_restaurant"),
    ("f_n_b", "specialty_tags", "oyster_bar_restaurant"),
    ("f_n_b", "specialty_tags", "steakhouse"),
    ("f_n_b", "specialty_tags", "bakery"),
    ("f_n_b", "specialty_tags", "pastry_shop"),
    ("f_n_b", "specialty_tags", "cake_shop"),
})
LEGACY_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z][A-Za-z0-9]*)? = true|types\[\] = .+")


def resolve_condition(sector, group, raw):
    """(sector, group, amenity_raw) -> (kind, path, giá trị) hoặc None. Dòng ngoài FLAG_MATCH / TYPE_MATCH không khớp.
    Ví dụ ("accommodation", "general_amenities", "outdoorSeating") -> ("flag", "flags.outdoorSeating", "true")."""
    key = (sector, group, (raw or "").strip())
    if key in TYPE_MATCH:
        return ("type", TYPES_PATH, key[2])
    if key not in FLAG_MATCH:
        return None
    head, _, leaf = key[2].partition(".")
    if not leaf:
        return ("flag", f"flags.{head}", "true") if head in FLAG_KEYS else None
    return ("flag", f"{head}.{leaf}", "true") if head in OBJECT_KEYS else None


def is_legacy_form(raw):
    """amenity_raw còn dạng cũ (key = true hoặc types[] = ...): seed chưa chạy lại full."""
    return LEGACY_RE.fullmatch((raw or "").strip()) is not None


def match_conditions(rows):
    """rows: (business_sector, amenity_group, amenity_raw, amenity, amenity_vi) google active.
    Output: (điều kiện = 5 cột + kind, path, giá trị ; khoá 3 cột trùng ; số dòng dạng cũ)."""
    conds = [tuple(r) + hit for r in rows if (hit := resolve_condition(r[0], r[1], r[2]))]
    seen = {}
    for c in conds:
        seen[c[:3]] = seen.get(c[:3], 0) + 1
    dup = sorted(k for k, n in seen.items() if n > 1)
    return conds, dup, sum(is_legacy_form(r[2]) for r in rows)
# END_AMENITY_MATCH
```

### E5. Build cell (`d1amenbuild`; `SPEC` unchanged)

Remove `from collections import Counter`. Replace `COND_SCHEMA` and `build`:

```python
COND_SCHEMA = ("business_sector string, amenity_group string, amenity_raw string, amenity string, "
               "amenity_vi string, _kind string, _path string, _v string")


def build(ctx: NodeContext) -> DataFrame:
    # Từ điển google active -> điều kiện khớp. Chỉ key trong FLAG_MATCH / TYPE_MATCH; dòng khác (kể cả dạng cũ) bỏ qua.
    rows = [tuple(r) for r in (ctx.input("dict")
            .where((F.lower(F.trim("source_name")) == GOOGLE) & (F.col("is_active") == F.lit(True)))
            .select("business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_vi").collect())]
    conds, dup, legacy = match_conditions(rows)
    if dup:
        raise QualityGateError(f"ref_dictionary_amenities: key google trùng trong (business_sector, amenity_group) {dup}")
    if not conds:
        raise QualityGateError("ref_dictionary_amenities: không có key google khớp được")
    cond = F.broadcast(spark.createDataFrame(conds, COND_SCHEMA))
    # source_flags_json = {"flags": {...}, "parkingOptions": {...} | null, ...}; object null -> không nổ dòng.
    src = ctx.input("amenity").select("poi_id", "source_flags_json")
    top = src.select("poi_id", F.explode(F.from_json("source_flags_json", "map<string,string>")).alias("_top", "_obj"))
    flat = (top.select("poi_id", "_top", F.explode(F.from_json("_obj", "map<string,string>")).alias("_leaf", "_v"))
               .select("poi_id", F.concat_ws(".", "_top", "_leaf").alias("_path"), "_v"))
    ent = ctx.input("entity").select("poi_id", "business_sector", "source_name", "types_json")
    flags = flat.join(ent.select("poi_id", "business_sector"), "poi_id").select("poi_id", "business_sector", "_path", "_v")
    # types_json = ["bakery", "cafe", ...] của POI google; phần tử lặp chỉ tính 1 lần.
    types = (ent.where(F.lower(F.trim("source_name")) == GOOGLE)
                .select("poi_id", "business_sector", F.lit(TYPES_PATH).alias("_path"),
                        F.explode(F.from_json("types_json", "array<string>")).alias("_v"))
                .dropDuplicates(["poi_id", "_v"]))
    out = flags.unionByName(types).join(cond, ["business_sector", "_path", "_v"])
    src_rows = src.count()
    unparsed = src.where(F.col("source_flags_json").isNotNull()
                         & F.from_json("source_flags_json", "map<string,string>").isNull()).count()
    joined = src.join(ent.select("poi_id"), "poi_id").count()
    by_kind = {r["_kind"]: r["count"] for r in out.groupBy("_kind").count().collect()}
    n = sum(by_kind.values())
    n_flag = sum(c[5] == "flag" for c in conds)
    ctx.metrics.update(src_rows=src_rows, pois_joined=joined, pois_without_entity=src_rows - joined,
                       unparsed_json=unparsed, dict_google_active=len(rows), dict_legacy_form=legacy,
                       conditions_matchable=len(conds), conditions_flag=n_flag, conditions_type=len(conds) - n_flag,
                       conditions_skipped=len(rows) - len(conds),
                       rows_flag=by_kind.get("flag", 0), rows_type=by_kind.get("type", 0), rows=n)
    # Không có dòng khớp là trạng thái hợp lệ: DataFrame rỗng để RECOMPUTE soft-delete amenity cũ.
    return out.select(*OUT_COLS)
```

`d1amenmd` text: "RECOMPUTE `lh_vv_silver.dbo.slv_poi_amenity`. Key cờ google khớp `source_flags_json` = true; key tách từ `types[]` khớp đúng một phần tử `types_json` của `slv_poi_entity_non_enrich`. `business_sector` từ `slv_poi_entity_non_enrich`."

### E6. Docs (`docs/context/01_DATA_MODEL.md`)

- §6 N7, column "Quyết định nằm ở đây": replace "Khớp `source_flags_json` với điều kiện google `path = true/false`." with "Khớp key cờ google (`amenity_raw` chỉ còn key, ví dụ `outdoorSeating`) với `source_flags_json` = true; key tách từ `types[]` khớp đúng một phần tử `types_json` của `slv_poi_entity_non_enrich`. Dòng google khác không khớp. Danh sách key khớp ghim trong `NB_SLV_POI_AMENITY` (`FLAG_MATCH` 27, `TYPE_MATCH` 14)." Keep the rest of the cell.
- §6.1 `ref_dictionary_amenities` "Seed hiện có": "158 dòng: 84 `google` + 74 `partner`, seed insert-only từ `mapping_amenities.md`; `amenity_raw` chỉ còn key (`key = true` → `key`, `types[] = a, b` → 2 dòng). Đổi seed cần chạy lại full theo runbook".

### E7. Tests (`tests/test_poi_amenity_contract.py`)

Keep `parse_mapping`, `clean`, `_nb`, `_between`, `_seed_ns`, `_match_ns`. Remove the module-level `COND_RE`/`resolve_condition` copy. Replace `MATCHABLE` with test-owned oracles `FLAG_MATCH` (the 27 tuples of E4) and `TYPE_MATCH` (the 14 of E4). Add `_google(rows) -> [(sec, grp, raw, en, vi) ...]` and `_expand(rows, keys)`.

| Test | Asserts |
|---|---|
| `test_seed_matches_mapping_file` | `SEED_ROWS == _expand(parse_mapping(md), ns["amenity_keys"])`; `validate_seed(SEED_ROWS)` passes |
| `test_amenity_keys_cases` | `outdoorSeating = true`→`[outdoorSeating]`; `parkingOptions.freeElectricVehicleParking = true`→`[parkingOptions.freeElectricVehicleParking]`; `types[] = hot_spring, sauna`→`[hot_spring, sauna]`; `types[] = bakery, pastry_shop, cake_shop`→3 keys; unchanged: `types[] có art_gallery`, `types[] thuộc business_category = Bar & Pub/Nightlife`, `outdoorSeating = true = true`, `serves_meals = true`, `parkingOptions.freeParkingLot, parkingOptions.paidParkingLot = true`, `cat_cafe, dog_cafe`, `dim_sum_restaurant`, `Hồ bơi`; idempotent on every seed raw |
| `test_seed_census` | Over the md rows: 27 flag, 8 types → 14 keys, 117 unchanged; every partner row unchanged |
| `test_seed_counts` | 158 total; partner 74; google 84; per (sector, source): acc partner 22 / google 31, f_n_b 18 / 34, attraction 22 / 16, shopping 12 / 3 |
| `test_seed_split_rows_keep_columns` | `hot_spring` and `sauna` both `('google','accommodation','general_amenities',_, 'Sauna','Xông hơi')`; `bakery`/`pastry_shop`/`cake_shop` share `('Bakery','Tiệm bánh')` |
| `test_seed_excludes_placeholders` | As now, with `parkingOptions.freeStreetParking` (no suffix) |
| `test_seed_raw_unique_within_group` | 4-column duplicates == `AMENITY_SHARED_RAW` exactly, count 2; `validate_seed(SEED_ROWS + [('google','accommodation','general_amenities','sauna','Steam','Hơi')])` raises; `validate_seed` raises on a row with `outdoorSeating = true` |
| `test_hoac_split_same_amenity` | Unchanged (parking 2, EV 3) |
| `test_resolve_condition_cases` | flag `("accommodation","general_amenities","outdoorSeating")`→`("flag","flags.outdoorSeating","true")`; dotted → `("flag","parkingOptions.freeStreetParking","true")`; type `("f_n_b","specialty_tags","bakery")`→`("type","types[]","bakery")`; None for attraction `restroom`/`goodForChildren`/`accessibilityOptions.wheelchairAccessibleEntrance`, shopping `delivery`, f_n_b `dim_sum_restaurant`, accommodation `outdoorSeating = true`, f_n_b `outdoorSeating = true = true` |
| `test_match_sets_pinned` | ns `FLAG_MATCH` == oracle == {md flag-form google rows, stripped}; ns `TYPE_MATCH` == oracle == {split keys of md types rows}; sizes 27/14; disjoint; `AMENITY_SHARED_RAW` keys not in either; both ⊆ seed google 4-column keys; every `FLAG_MATCH` key resolves |
| `test_legacy_form_consistent` | For every md raw: `is_legacy_form(raw) == (amenity_keys(raw) != [raw])`; no seed raw is legacy |
| `test_match_conditions_states` | New seed google → 41 conds, 27 flag, dup `[]`, legacy 0; old md google rows only → conds `[]` (fails closed); old + new → 41 conds, dup `[]`, legacy 35; new + duplicate `('accommodation','general_amenities','sauna','Steam','Hơi')` → dup `[('accommodation','general_amenities','sauna')]` |
| `test_flag_keys_match_registry` | Unchanged |
| `test_amenity_node_contract` | Existing asserts, plus `'"array<string>"' in src`, `"types_json" in src`, `"dropDuplicates" in src`, `"TYPES_PATH" in src`, `"dict_legacy_form=" in src`, `"conditions_type=" in src`; still no `explode_outer` / `get_json_object` / `business_category` |
| `test_setup_contract` | Existing asserts, plus `"stale_keys" in src` and `'"stale": STALE' in src` |

`tests/test_initial_ddl_contract.py`: run unchanged. `test_*` with `_marker(... "# BEGIN_AMENITY_SEED" ...)` equality and `AMENITY_ROWS = list(SEED_ROWS)` must pass.

## 19. Runtime runbook design (user-run on Fabric DEV after review PASS)

Run from a scratch DEV notebook that starts with `%run NB_LIB_TRANSFORM_SLV_GLD`. `PL = "PL_VV_TRANS_SLV_TO_SLV_1H"`. Record every output in `runtime-runbook.md` evidence (aggregates only).

R0. Preconditions:
- DEV notebooks match the merged commit.
- `NB_SETUP_POI_AMENITY` `p_apply=false` exits PLAN with `google=84`, `partner=74`, `entity_edges_ok=5`. Record `stale_keys` (expected 35 if DEV equals the old seed).
- PL has no trigger, and the lock row `lock_exec_id` is NULL.

R1. Baseline (read-only):
- `DESCRIBE HISTORY` → latest `V_dict0`, `V_amen0`; also the latest versions of `slv_3p_poi_amenity` and `slv_poi_entity_non_enrich`.
- Dictionary: count by `source_name`; `is_active = false` count; rows not in the new seed (`stale_keys`) split into legacy form (`amenity_raw LIKE '% = true'` or `LIKE 'types[] = %'`) and other.
- Amenity: total, live (`deleted_at IS NULL`), soft-deleted, live by `amenity_raw LIKE '% = true'`, distinct live `poi_id`.
- Edges: `SELECT src_tbl, is_active, count(*) FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config WHERE pl_name = PL AND trg_tbl = 'slv_poi_amenity' GROUP BY src_tbl, is_active`.

R1b. Backup: `CREATE TABLE lh_vv_silver.dbo.bak_ref_dictionary_amenities_20261019 AS SELECT * FROM ...` and the same for `bak_slv_poi_amenity_20261019`. Each backup count must equal the baseline.

**STOP R1 (user decision):** continue only if non-legacy stale dictionary rows = 0, `is_active = false` = 0, drift = 0, and edges = 3 active plus the retired `slv_poi_entity` row (if present), each pair once. Otherwise the user decides, because manual DEV edits would be lost.

R2. Dictionary reload:
- Under `acquire_flow_lock(PL, X, X, LOCK_TIMEOUT_DEFAULT_MIN)` with `finally: release_flow_lock`: `DELETE FROM lh_vv_silver.dbo.ref_dictionary_amenities`.
- Run `NB_SETUP_POI_AMENITY` `p_apply=true`. Expect `inserted=158`, `drift=0`, `stale=0`, `edges_inserted=0`, `edges_retired=0`.
- Checks: count 158 (84/74); 5-column duplicates 0; 4-column duplicates = the one shared key with n=2; the edge query equals R1; a PLAN rerun gives `missing_keys=0`, `stale_keys=0`.

**STOP R2 (evidence).**

R3. Amenity rebuild:
- Run `NB_SLV_POI_AMENITY` `p_mode=DRY_RUN`, `p_force=true`. Expect the metrics of §15, and a diff with soft-delete = baseline live rows and insert = `rows`.
- Under the lock: `DELETE FROM lh_vv_silver.dbo.slv_poi_amenity`.
- Run `NB_SLV_POI_AMENITY` `p_mode=RUN`, `p_force=true`. Expect SUCCESS and the same metrics.
- Checks: all `deleted_at IS NULL`; primary key unique; no `amenity_raw LIKE '% = true'` or `LIKE 'types[] = %'`; `rows_flag` per `(business_sector, amenity_group, amenity_raw)` equals the backup's live counts per `(business_sector, amenity_group, substring(amenity_raw, 1, length(amenity_raw) - 7))`. This is a hard check if the input versions equal R1; otherwise report the difference. Report `rows_type` (expected > 0; 0 is a warning, not a failure). Report the total versus the baseline live count. The edge query equals R1.

**STOP R3 (user acceptance):** the user accepts, or runs the rollback in §17. Backup tables stay until the user decides to remove them. Removing them is outside this runbook.

## 20. Verification

- Local: `python -m pytest tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py -q`, then `python -m pytest tests -q`. All green, with no skipped tests in these two files.
- Review focus: sql-data (seed census, stale/backup SQL, RESTORE), spark-runtime (`explode` + `dropDuplicates`, broadcast condition, extra `groupBy` action), state-correctness (I8–I11, fail-closed transitions, insert-only rerun), risk-gate (§13, §17, §19 stops).
- Runtime: §19 R0–R3 evidence. `gates.runtime` is set only from the user's result, never by an agent.

## 21. Residual risks and follow-ups

- Matching rules now live partly in code (A1). Backlog: a `match_kind` column with model design, so rules become data again.
- The `goodForChildren` pair under attraction stays as two dictionary rows, and neither matches (A3). Changing that is a user decision on seed content.
- Type keys match `slv_poi_entity_non_enrich.types_json` for every google entity POI, including POIs with no `slv_3p_poi_amenity` row. This is intended: types belong to the POI.
- RESTORE depends on Delta file retention. The CTAS backups cover the case where it fails.
