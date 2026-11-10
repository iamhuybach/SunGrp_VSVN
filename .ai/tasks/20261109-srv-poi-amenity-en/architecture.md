RESULT: PASS

## Main brief

### Decision
PASS. U-1, U-2, and U-3 are closed in `decision.md`. M-1 and M-2 are done.
- `amenity = amenity_code(amenity_en)`: NFKD, drop combining marks, split camelCase, lowercase, `[\W_]+`→`_`, strip `_`. `SEED_ROWS` stays as 7-tuples, and field 5 is now `amenity_en`.
- `amenity_en` goes right after `amenity` in every layer. It is NOT NULL in `ref` and nullable in slv, gold, and PostgreSQL.
- slv is migrated with `ALTER ... ADD COLUMNS (amenity_en STRING AFTER amenity)`. The user DROPs and recreates `ref`, gold, and PostgreSQL.
- The API keeps its path, binds neither `lang` nor `Accept-Language`, and returns the D-01 tree in a fixed order. `service_flags` reads the `service_flags` column (U-2).

### Invariants Main must preserve
- `ref.amenity_en` equals seed field 5, and `ref.amenity` equals `amenity_code(amenity_en)`. Every code fully matches `^[a-z0-9]+(_[a-z0-9]+)*$`, and the 5-column key with codes is unique. `validate_seed` enforces both.
- slv, gold, and PostgreSQL share this column order: `poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags, row_hash, created_at, updated_at, deleted_at`. The PKs are unchanged.
- The gold `OUT_COLS` equals the slv `OUT_COLS`, and the gold `build` stays `select(*OUT_COLS)`.
- The slv build raises before any write if `ref` lacks STRING `amenity_en`, or if an active google row has a blank `amenity` or `amenity_en`.
- `c1setupddl` runs in this order: raise if `ref` exists without `amenity_en`, then ALTER slv, then CREATE IF NOT EXISTS, then compare against `EXPECTED`.
- The setup MERGE stays insert-only, with no `WHEN MATCHED`.
- The `BEGIN/END_AMENITY_SEED` block, including `import unicodedata`, is byte-identical in `c1setupseed` and `init_seed_amenity`. `AMENITY_ROWS = list(SEED_ROWS)` is unchanged.
- The slv build tuple tail stays `service_flags, _kind, _path, _v`. The `conditions_service_flags` metric reads `c[-4]`.
- JSON items map with no fallback: `amenity_code`←`amenity`, `amenity_label_en`←`amenity_en`, `amenity_label_vi`←`amenity_vi`, `service_flags`←`service_flags`. There is no `data[].amenity_vi`, no `amenity_label`, and no `GENERAL` fallback.
- Groups sort by `amenity_group` ascending. Items sort by `amenity_code` ascending (nulls last), then `amenity_raw`. The `json_type` filter stays.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupseed` inside the markers | Add `import unicodedata`, `AMENITY_CAMEL_RE`, `AMENITY_CODE_RE`, `AMENITY_CODE_SHAPE`, `amenity_code`, `amenity_seed_rows`. In `validate_seed`, rename field 5 to `amenity_en` and add the shape and key checks (full doc "Seed block") | T-1, T-2 green |
| 2 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_amenity` | Byte-identical copy of the row 1 block | `test_initial_ddl_contract` green |
| 3 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupplan` | 8-column `SEED_SCHEMA`; `createDataFrame(amenity_seed_rows(SEED_ROWS), ...)`; add `ref_has_amenity_en` and `slv_has_amenity_en` to the print and the PLAN JSON | Both keys are in the PLAN JSON |
| 4 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupddl` | `ref` guard; guarded `ALTER ... AFTER amenity`; `amenity_en` in both CREATE statements (`NOT NULL` in `ref`) and both `EXPECTED` lists (full doc "c1setupddl") | T-4 setup asserts green |
| 5 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupmerge` | Add `amenity_en` to the INSERT columns and values; add `t.amenity_en <=> s.amenity_en` to the DRIFT SQL | `WHEN MATCHED` still absent |
| 6 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` `TABLE_SPECS` | Add `amenity_en` after `amenity`: NOT NULL in `ref` (same encoding as `amenity`), `None` in slv and gold | T-5 green |
| 7 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_plan` `_v_setup_amenities` | `amenity_seed_rows(AMENITY_ROWS)` plus the 8-column schema string | The view has `amenity_en` |
| 8 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_write` `_merge_amenities` and drift SQL | Add `amenity_en` | Key lists unchanged |
| 9 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenbuild` | `COND_SCHEMA` and `OUT_COLS` with `amenity_en` after `amenity`; dtype guard; select order; blank guard plus the `dict_amenity_en_blank` metric; `c[5]`→`c[-4]` (full doc "NB_SLV_POI_AMENITY d1amenbuild") | T-3, T-4 green |
| 10 | notebooks/NB_GLD_SRV_POI_AMENITY.ipynb | `srvamenitybuild` `OUT_COLS` | Same tuple as slv | `test_poi_media_amenity_contract` green |
| 11 | notebooks/NB_CREATE_DDL.ipynb | `amenddlpy` `AMENITY_COLS`; `amenddlmd` | Add `('amenity_en','STRING')` after `amenity`; add a one-line note that the old table must be DROPped | T-5 green |
| 12 | sql/postgres/gld_srv_serve.pg.sql | `CREATE TABLE apps.srv_poi_amenity` | Add `amenity_en text,` after `amenity text,` | `test_gold_and_pg_columns_and_types_match` green |
| 13 | tests/test_poi_amenity_contract.py | new T-1, T-2, T-3; update `test_amenity_node_contract`, `test_setup_contract` | See full doc "Verification" | pytest green |
| 14 | tests/test_srv_poi_serving_contract.py | new `test_amenity_en_order_across_layers` | T-5 | pytest green |
| 15 | services/.../domain/entity/SrvPoiAmenity.java | field after `amenity` | Add `@Column(name = "amenity_en") private String amenityEn;` and its getter | `test_entities_match_gold_columns_types_and_keys` green |
| 16 | services/.../api/dto/PoiAmenityGroupResponse.java | record | Fields `amenity_group` and `items`; `Item` has `amenity_code`, `amenity_label_en`, `amenity_label_vi`, `service_flags`; `JsonInclude.ALWAYS` (full doc "Java") | T-7 green |
| 17 | services/.../service/PoiService.java | `getAmenities`; `AMENITY_GROUP_LABELS_*` | Delete both label maps, the 2-arg overload, and the fallbacks; add one 1-arg method with the sort and the I-10 mapping | T-6 green |
| 18 | services/.../api/PoiController.java | `getAmenities` | Remove the `lang` and `Accept-Language` params; call `getAmenities(poiId)` | T-7 green |
| 19 | services/.../test/.../service/PoiServiceTest.java | amenities tests | T-6 | mvn green |
| 20 | services/.../test/.../api/PoiControllerIntegrationTest.java | amenities tests | T-7 | mvn green |
| 21 | tests/test_poi_media_amenity_contract.py | `AMENITY_COLS` | Add `("amenity_en","STRING",None)` after `amenity` | pytest green |
| 22 | docs/context/mapping_gld_srv_poi_amenity.md | §0, §1 | `amenity_en` column; RULE-U1; JSON-to-column table; migration note | Done before review |
| 23 | docs/context/01_DATA_MODEL.md | rows `ref_dictionary_amenities`, N7 `slv_poi_amenity` | Add `amenity_en` and the snake_case note | Done before review |
| 24 | docs/context/api-mapping/amenities.md (only after S-1) | request and response tables, sample | Remove `lang`, `Accept-Language`, `amenity_vi`, `amenity_label`, and the fallbacks; add the D-01 fields | Done before review |

`SrvPoiAmenityRepository.java` and `PoiAmenityId.java` need no change.

### Order and stop points
1. STOP S-1 (Main scope decision, does not block rows 1–23): `docs/context/api-mapping/amenities.md` documents the old `lang`/`amenity_label` contract and is not in `scope.files`. Add it to scope (recommended), or record a backlog item in `decision.md`.
2. Edit rows 1, 2, and 13 (seed and seed tests). Run the targeted pytest. The seed must validate before anything else changes.
3. Edit rows 3–11, 14, and 21. Run the targeted pytest, then `pytest tests -q`.
4. Edit rows 12 and 15–20. Run mvn.
5. Edit rows 22–23, plus row 24 if S-1 added the file. Request specialist review.
6. STOP S-2 (runtime evidence, user-run): runbook steps R-0 to R-9 and proofs P-1 to P-7 (full doc "Rollout", "Verification" → "Runtime proof"). The agent runs no Fabric, DROP, Copy Job, or docker steps.
7. STOP S-3 (user decision, only if P-2 fails because Fabric rejects `ADD COLUMNS ... AFTER`): approve a DROP of slv and a setup rerun. That loses `created_at` and resets `NB_ENR_POI_INFO` change detection.

### Tests and verification
- `python -m pytest tests/test_poi_amenity_contract.py tests/test_srv_poi_serving_contract.py tests/test_poi_media_amenity_contract.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py tests/test_enr_poi_contract.py -q`
- `python -m pytest tests -q`
- `cd services/data-serving-service && mvnw.cmd -q -B test`
- New Python tests: `test_amenity_code_rule_cases` (includes `Pet Café`→`pet_cafe`, NFD `Café`, `servesWine`→`serves_wine`, `pureServiceAreaBusiness`, `acceptsNfc`, `takeout`, `""`, `None`), `test_seed_rows_with_code_shape` (175 rows; shape; key uniqueness; raises on `Đỗ` and on a duplicate), `test_match_conditions_carries_amenity_en`, `test_amenity_en_order_across_layers`.
- Updated Python tests: `test_amenity_node_contract`, `test_setup_contract`, `AMENITY_COLS` in `test_poi_media_amenity_contract.py`.
- `PoiServiceTest` tests: `shouldMapAmenityColumnsToD01Fields` (`service_flags` differs from `amenity_vi`), `shouldOrderAmenityGroupsAndItemsDeterministically`, `shouldFilterJsonTypeAmenityRows`, plus the existing empty and 404 tests with the 1-arg call.
- `PoiControllerIntegrationTest` tests: `shouldReturnAmenitiesSuccessfully` (D-01 paths; `amenity_vi` and `amenity_label` absent), `shouldIgnoreLangQueryAndAcceptLanguageForAmenities`.
- These must stay green without edits: `test_seed_matches_mapping_file`, `test_amenity_keys_cases`, `test_amenity_ddl_matches_node`, `test_gold_and_pg_columns_and_types_match`, `test_entities_match_gold_columns_types_and_keys`, `DataServingApplicationTests`.

### Read only if needed
- "Verdict and closed items": S-1 and the seed facts behind T-1 and T-2
- "Grain and keys": rows 1, 4, 6, 9 (model conflicts 2, 5, 6, 7a, 7b)
- "Implementation plan" → "Seed block", "c1setupplan", "c1setupddl", "c1setupmerge": rows 1–5
- "Implementation plan" → "NB_SETUP_INITIAL_DDL": rows 2, 6–8
- "Implementation plan" → "NB_SLV_POI_AMENITY d1amenbuild": row 9
- "Implementation plan" → "Gold", "PostgreSQL": rows 10–12
- "Implementation plan" → "Java": rows 15–18
- "Implementation plan" → "Documentation": rows 22–24
- "Ordering", "Concurrency", "Partial failure", "Retry and recovery", "Rollout", "Rollback and forward recovery": S-2, S-3, runbook
- "Alternatives considered": why the code is computed, NFKD fold, DROP `ref`, ALTER slv, service-side sort
- "Verification": rows 13, 14, 19–21; P-1 to P-7 SQL

# Architecture: 20261109-srv-poi-amenity-en (round 2)

## Verdict and closed items

Round 1 blocked on U-1, U-2, U-3, M-1, and M-2. All five are now closed:

| ID | Closed by | Effect on this design |
|---|---|---|
| U-1 | `decision.md` U-1: option B plus folding accented letters such as `é` to `e` | RULE-U1 below. `amenity = amenity_code(amenity_en)`. |
| U-2 | `decision.md` U-2: `srv_poi_amenity.service_flags` | JSON `items[].service_flags` reads column `service_flags`. |
| U-3 | `decision.md` U-3: the user DROPs `ref_dictionary_amenities` and reruns `NB_SETUP_POI_AMENITY p_apply=true` | Runbook step R-3. `ref.amenity_en` is NOT NULL (model-design `## Columns`). |
| M-1 | `scope.files` now has `tests/test_poi_media_amenity_contract.py`, `PoiControllerIntegrationTest.java`, and `docs/context/01_DATA_MODEL.md` | Edit rows 20, 21, 23. |
| M-2 | `model-design.md` round 2 records U-1 to U-3 and the column position | Grain and keys are cited from it. |

Facts I checked against the repo this round:
- The seed has 175 rows (`SEED_ROWS` in `c1setupseed`).
- Field 5 (`amenity_en`) has exactly one non-ASCII letter: `Pet Café`, on the `cat_cafe, dog_cafe` row.
- The only camelCase values are the `google/other/other` rows: `curbsidePickup`, `servesBreakfast`, `servesLunch`, `servesDinner`, `servesBeer`, `servesWine`, `servesBrunch`, `servesVegetarianFood`, `menuForChildren`, `servesDessert`, `servesCoffee`, `allowsDogs`, `pureServiceAreaBusiness`, `acceptsDebitCards`, `acceptsNfc`. Each has only lowercase-to-uppercase boundaries.
- Two values are already snake_case and keep their key: `takeout` and `reservable`.
- A gap round 1 did not cover: `docs/context/api-mapping/amenities.md` documents the current API (`lang`, `Accept-Language`, `data[].amenity_vi`, `amenity_label`, `GENERAL` fallback). This change makes it stale, and it is not in `scope.files`. This does not block the design. Main either adds it to scope (recommended, row 24) or records a backlog item (stop S-1).

## Scope

- `lh_vv_silver.dbo.ref_dictionary_amenities`:
  - Add `amenity_en STRING NOT NULL`. It holds the current display string, which is seed field 5.
  - `amenity` becomes `amenity_code(amenity_en)` (RULE-U1).
  - The DDL and seed are in `NB_SETUP_POI_AMENITY`, mirrored in `NB_SETUP_INITIAL_DDL`.
- `lh_vv_silver.dbo.slv_poi_amenity` (`NB_SLV_POI_AMENITY`):
  - Carry `amenity_en` from the matched dictionary row.
  - Migrate the existing table in place with `ADD COLUMNS (amenity_en STRING AFTER amenity)`.
- `lh_vv_gold.dbo.gld_srv_poi_amenity`:
  - Add `amenity_en` to `OUT_COLS`, `AMENITY_COLS` (`NB_CREATE_DDL` `amenddlpy`), and `TABLE_SPECS`.
  - The user runs the DROP and re-init.
- `apps.srv_poi_amenity`:
  - Add `amenity_en text` after `amenity` in `sql/postgres/gld_srv_serve.pg.sql`.
  - The user runs DROP, CREATE, and the Copy Job.
- API `GET /api/v1/pois/{poi_id}/amenities`:
  - The path is unchanged (D-02).
  - Remove the `lang` query and the `Accept-Language` binding.
  - Return the D-01 tree with the U-2 mapping.
- Docs:
  - `docs/context/mapping_gld_srv_poi_amenity.md`
  - `docs/context/01_DATA_MODEL.md`
  - `docs/context/api-mapping/amenities.md`, if Main adds it to scope (S-1)

## Non-goals

- Grain and keys stay as they are (model-design `## Keys`).
- No change to matching (`FLAG_MATCH`, `TYPE_MATCH`, `JSON_MATCH`, `amenity_keys`, `# BEGIN_AMENITY_MATCH`). Matching reads `amenity_raw`, not `amenity`.
- The existing API filter that drops `amenity_raw` rows containing `json_type` stays.
- Items that share an `amenity_code` inside a group are not deduplicated. Example: `freeElectricVehicleParking` and `paidElectricVehicleParking` both give `ev_charging_station`. That already happens today.
- No group display label. D-01 removes `data[].amenity_vi`.
- No pipeline JSON, lock, watermark, CDC, or `ctrl_cfg_schema_registry` change.
- No `NB_ENR_POI_INFO` change. It reads only `poi_id` and `service_flags`.
- No rule for `đ`, Vietnamese, digit-to-uppercase, or acronym-to-word boundaries. The seed `amenity_en` has none of these. The shape check fails closed if a future seed adds one.
- The agent runs no Fabric, DROP, Copy Job, or docker steps, and does not read `docs/poi-serving-api/`.

## Invariants

- I-1: `ref.amenity_en` equals seed field 5, which `SEED_ROWS` keeps as a 7-tuple. `ref.amenity` equals `amenity_code(ref.amenity_en)`.
- I-2: Every seed code fully matches `^[a-z0-9]+(_[a-z0-9]+)*$`, so it is non-empty, ASCII, and idempotent. `validate_seed` enforces this.
- I-3: The 5-column `ref` key, computed with the code, is unique across the seed. `validate_seed` enforces this. The 4-column duplicates stay limited to `AMENITY_SHARED_RAW`, whose codes are `good_for_children` and `family_friendly`.
- I-4: The existing `match_conditions` duplicate check stays. It fails closed if two active google rows match the same condition.
- I-5: slv, gold, and PostgreSQL use this column order: `poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags, row_hash, created_at, updated_at, deleted_at`. The PKs are unchanged.
- I-6: The gold `OUT_COLS` equals the slv `OUT_COLS`, and the gold `build` stays `select(*OUT_COLS)`.
- I-7: `NB_SLV_POI_AMENITY` raises before any write if `ref` lacks `amenity_en` as STRING, or if any active google row has a blank `amenity` or `amenity_en`.
- I-8: `c1setupddl` runs in this order:
  1. Raise `ConfigError` if `ref` exists without `amenity_en`. No write has happened yet.
  2. ALTER slv.
  3. CREATE IF NOT EXISTS.
  4. Compare against `EXPECTED`.
- I-9: The setup MERGE stays insert-only, with no `WHEN MATCHED`. The `BEGIN/END_AMENITY_SEED` block is byte-identical in `c1setupseed` and `init_seed_amenity`, and `AMENITY_ROWS = list(SEED_ROWS)`.
- I-10: The API has no `lang` or `Accept-Language` binding. The JSON item fields map without fallback:
  - `amenity_code` ← `amenity`
  - `amenity_label_en` ← `amenity_en`
  - `amenity_label_vi` ← `amenity_vi`
  - `service_flags` ← `service_flags` (U-2)

  The response has no `data[].amenity_vi` and no `amenity_label`. Groups are sorted by `amenity_group` ascending. Items are sorted by `amenity_code` ascending (nulls last), then `amenity_raw`.

## State ownership

| State | Writer | Readers |
|---|---|---|
| `ref_dictionary_amenities` | `NB_SETUP_POI_AMENITY` `c1setupmerge`; `NB_SETUP_INITIAL_DDL` `_merge_amenities` (insert-only) | `NB_SLV_POI_AMENITY` |
| `slv_poi_amenity` data | `NB_SLV_POI_AMENITY` (`run_node`, MERGE on PK) | `NB_GLD_SRV_POI_AMENITY`, `NB_ENR_POI_INFO` |
| `slv_poi_amenity` schema | `c1setupddl` (CREATE plus the new guarded ALTER) | contract tests |
| `gld_srv_poi_amenity` schema | `NB_CREATE_DDL` `amenddlpy`; `NB_SETUP_INITIAL_DDL` for a fresh environment | |
| `gld_srv_poi_amenity` data | `NB_GLD_SRV_POI_AMENITY` | Copy Job |
| `apps.srv_poi_amenity` | User: DDL from `gld_srv_serve.pg.sql`, then the Copy Job | `data-serving-service`, read-only |

## Grain and keys

See model-design `## Entities and grain` and `## Keys`. Grain and keys are unchanged at every layer. Only the values of the `ref` key column `amenity` change.

Model-design conflicts resolved here:
- Conflict 2: RULE-U1, implemented as `amenity_code` (see "Seed block"). It uses this step order:
  1. NFKD.
  2. Drop combining marks.
  3. Split camelCase at lowercase-to-uppercase.
  4. Lowercase.
  5. Replace each run of `[\W_]+` with `_`.
  6. Strip `_` at both ends.

  Model-design lists the fold last. Folding first gives the same output for all 175 seed rows, and it stops a stray combining mark from becoming `_`. T-2 asserts every row.
- Conflict 5: `ref.amenity_en` is NOT NULL. In slv, gold, and PostgreSQL it is nullable, matching `amenity`. I-7 enforces non-blank values in code.
- Conflict 6: `amenity_en` goes directly after `amenity` in every list. Existing slv gets it through `ALTER ... AFTER amenity`, because `ensure_target` would append it after `deleted_at` and break the ordered `EXPECTED` check.
- Conflict 7a: the slv build selects `amenity_en` after `amenity`. The tuple tail stays `service_flags, _kind, _path, _v`, and metrics read `service_flags` as `c[-4]` instead of `c[5]`.
- Conflict 7b: the only writer of `apps.srv_poi_amenity` is the user-run Copy Job. No notebook in the repo writes it. R-7 checks that the Copy Job column mapping includes `amenity_en`.

## Ordering

- Setup cells, in the existing order:
  1. `c1setupseed`: validate.
  2. `c1setupplan`: exit if `p_apply=false`.
  3. `c1setupddl` (I-8).
  4. `c1setupmerge`.
  5. `c1setupedges`.
- Runtime: `ref` → slv → gold → PostgreSQL → API (see "Rollout").
- API: the service sorts with `Comparator.comparing(amenityGroup).thenComparing(amenity, nullsLast(naturalOrder())).thenComparing(amenityRaw)`, then groups into a `LinkedHashMap`. A POI has fewer than 100 rows, so a database `ORDER BY` adds nothing.

## Transaction and commit boundaries

- Each Delta statement is its own commit: ALTER slv, CREATE `ref`, the seed MERGE, the slv MERGE, and the gold MERGE. No transaction spans them. Correctness comes from ordering plus the fail-closed guards I-4, I-7, and I-8.
- slv: one `run_node` MERGE. Every live row except `takeout`/`reservable` matches gets a new `row_hash`, because `amenity` and `amenity_en` change. The first run updates nearly every row.
- Gold: `amenddlpy` creates the table under lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H`. Then one node MERGE fills it.
- PostgreSQL: the user runs `BEGIN; DROP TABLE apps.srv_poi_amenity; CREATE TABLE ...; COMMIT;`. The Copy Job then loads the data with its own commit semantics.
- API: `@Transactional(readOnly = true)`, with two queries: POI existence, then amenities.

## Idempotency

- `NB_SETUP_POI_AMENITY` rerun: the guard passes, the ALTER is skipped, CREATE IF NOT EXISTS does nothing, the insert-only MERGE inserts 0 rows, and `EXPECTED` passes.
- `amenddlpy` rerun: the schema already matches, and the edge insert is `WHERE NOT EXISTS`. Nothing changes.
- slv and gold node reruns: `row_hash` is unchanged, so no update happens.
- `amenity_code(amenity_code(x)) == amenity_code(x)`. T-1 asserts this.
- PostgreSQL CREATE is a one-time step the user runs. The Copy Job is a full reload, as today.

## Concurrency

- `PL_VV_TRANS_SLV_TO_ENR_15M` may run `NB_SLV_POI_AMENITY` while setup runs. There is no shared lock today, and this design adds none.
  - Delta optimistic concurrency serializes an ALTER and a MERGE on slv. The loser fails, and both writers can be rerun.
  - A slv run between the `ref` DROP and the reseed fails closed: the required input is missing, or `amenity_en` is missing (I-7).
- Between the gold DROP and `amenddlpy`, a 1H run could let `ensure_target` create gold with nullable key columns. `amenddlpy` would then stop with "lệch cột". R-1 pauses both triggers to close this window. Recovery: DROP gold and rerun `amenddlpy`.

## Retry and recovery

- Setup: the MERGE keeps `with_retry`. A failure partway through `c1setupddl` can be rerun, because every step is guarded.
- `ADD COLUMNS ... AFTER` is standard Delta DDL. Runtime proof P-2 confirms it on Fabric.
  - If Fabric rejects it, the cell fails before any `ref` CREATE, so nothing is written.
  - The fallback is a user-run DROP of slv, after which the setup recreates it in the right order. This loses slv `created_at` and resets `NB_ENR_POI_INFO` change detection, so it needs a user decision. Treat it as stop S-3, used only if P-2 fails.
- slv and gold nodes: the next pipeline cycle retries. Use `p_force="true"` for a manual rerun.

## Partial failure

| Failure point | State left | Effect | Recovery |
|---|---|---|---|
| Code synced, setup not run | Old `ref`, old slv schema | slv raises `ConfigError` (I-7). Gold raises `AnalysisException` on `amenity_en`. No writes. Serving keeps the old data. | R-2 to R-4 |
| `ref` dropped, reseed failed | `ref` missing or empty | slv fails on the required input or `match_coverage`. Fail closed. | Rerun the setup |
| slv altered, `ref` not reseeded | slv has a NULL `amenity_en` column | The setup guard raises (I-8). slv fails (I-7). Serving is unchanged. | DROP `ref`, rerun the setup |
| Gold dropped, not re-inited | No gold table | The 1H run may auto-create it with the wrong nullability. The Copy Job source is missing. | DROP gold, then `amenddlpy` |
| PostgreSQL dropped, Copy Job failed | Table empty | The old API returns `[]` | Rerun the Copy Job |
| New API deployed before the PostgreSQL migration | Entity selects a missing `amenity_en` | 500 on amenities only. `ddl-auto: none` keeps the app up. | Finish R-7 and R-8, or roll back the API |
| Copy Job mapping is explicit and lacks `amenity_en` | PostgreSQL `amenity_en` is NULL | `amenity_label_en` is null | Add the column to the mapping and rerun (P-6 catches this) |

## Observability

- slv metric `dict_amenity_en_blank`: the count of active google rows with a blank `amenity` or `amenity_en`. A value above 0 raises `QualityGateError` before the write. `conditions_service_flags` keeps its meaning through `c[-4]`.
- The setup plan print and the PLAN exit JSON add `ref_has_amenity_en` and `slv_has_amenity_en`.
- The setup drift SQL in both notebooks adds `t.amenity_en <=> s.amenity_en`.
- Plan mode against the old `ref` shows 173 new and 173 stale 5-column keys. `takeout` and `reservable` keep their key. After the DROP and reseed, both counts are 0.
- `NB_ENR_POI_INFO` sees one large change set the first time, because nearly every slv row updates. Its output values do not change, because it reads only `service_flags`. Expect a longer first 15M run.

## Security

- No new input surface. The API removes two inputs.
- `poi_id` stays a parameterized derived query.
- No PII, secret, or authorization change.
- Clients that still send `?lang=` or `Accept-Language` get 200 with the same `data`, because Spring ignores unbound query parameters and headers.

## Rollout

Every step is user-run. The runbook is written after implementation.

| Step | Action |
|---|---|
| R-0 | Record anchors: the latest version from `DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_amenity`, the gold row count, and the PostgreSQL row count. |
| R-1 | Pause the `PL_VV_TRANS_SLV_TO_ENR_15M` and `PL_VV_TRANS_SLV_TO_GLD_1H` triggers. Sync the notebooks to the workspace. |
| R-2 | `NB_SETUP_POI_AMENITY p_apply=false`. Expect `ref_has_amenity_en=false`, `slv_has_amenity_en=false`, and 173 new and 173 stale keys. |
| R-3 | U-3: `DROP TABLE lh_vv_silver.dbo.ref_dictionary_amenities`. |
| R-4 | `NB_SETUP_POI_AMENITY p_apply=true`. Expect `inserted=175 drift=0 stale=0`, and slv altered. Check P-1 and P-2. |
| R-5 | `DROP TABLE lh_vv_gold.dbo.gld_srv_poi_amenity`, then run `NB_CREATE_DDL` cell `amenddlpy` immediately. |
| R-6 | Run `NB_SLV_POI_AMENITY` (or the 15M pipeline) once. Then run `NB_GLD_SRV_POI_AMENITY` with `p_force=true` (or the 1H pipeline). Check P-3 to P-5. |
| R-7 | PostgreSQL: `BEGIN; DROP TABLE apps.srv_poi_amenity; <CREATE from gld_srv_serve.pg.sql>; COMMIT;`. Make sure the Copy Job column mapping includes `amenity_en`. |
| R-8 | Run the Copy Job. Check P-6. |
| R-9 | Deploy `data-serving-service`. Check P-7. Resume the triggers. |

## Rollback and forward recovery

- Forward recovery is the default. Every step can be rerun, and every failure fails closed.
- Full rollback, if the change is rejected:
  1. Revert the code.
  2. `RESTORE TABLE lh_vv_silver.dbo.slv_poi_amenity TO VERSION AS OF <R-0>`. This also reverts the schema, which the old `EXPECTED` check needs.
  3. DROP `ref` and rerun the old setup.
  4. DROP gold and run the old `amenddlpy`.
  5. Recreate the PostgreSQL table with the old DDL and run the Copy Job.
  6. Redeploy the old API.
- API-only rollback after the data migration is degraded but safe. The old API ignores `amenity_en`, and it shows the snake_case `amenity` as both the English label and the code.

## Alternatives considered

- A-1: seed literals per row instead of computing the code.
  - Rejected. It doubles the hand-maintained data in two byte-identical notebooks.
  - It also breaks `test_seed_matches_mapping_file`, which compares `row[:6]`.
  - A computed code keeps `SEED_ROWS` as 7-tuples.
- A-2: fold accents with a literal `translate('é'→'e')` instead of NFKD plus dropping combining marks.
  - Rejected. U-1 says "những kí tự như é", meaning letters like é, so a class rule fits better than a single literal.
  - NFKD handles every Latin accented letter.
  - Letters that do not decompose (`đ`) are not in the seed, and the I-2 shape check fails closed on them.
- A-3: reseed `ref` in place (deactivate stale rows and `ADD COLUMNS` on `ref`) instead of DROP and reseed.
  - Rejected. It makes the MERGE non-insert-only, which `test_setup_contract` forbids.
  - It also leaves 173 stale rows. U-3 chose DROP.
- A-4: DROP slv instead of `ALTER ... AFTER`.
  - Rejected. It loses `created_at` and resets `NB_ENR_POI_INFO` change detection.
  - It is kept only as the S-3 fallback.
- A-5: put `amenity_en` after `service_flags`.
  - Rejected. It saves one index change, `c[5]`, but still needs an ALTER.
  - Placing it after `amenity` keeps the code and its label together.
- A-6: sort in the repository instead of in the service.
  - Rejected. A service sort keeps `SrvPoiAmenityRepository` unchanged and needs no index.

## Implementation plan

The edit rows are numbered in the Main brief.

### Seed block (`c1setupseed`, mirrored byte-for-byte in `init_seed_amenity`) — rows 1, 2

- Add `import unicodedata` after `import re` inside the markers. The tests exec the block in isolation, so the import must be inside it.
- Add the following after `amenity_keys`:

```python
AMENITY_CAMEL_RE = re.compile(r"(?<=[a-z])(?=[A-Z])")
AMENITY_CODE_RE = re.compile(r"[\W_]+")
AMENITY_CODE_SHAPE = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)*")


def amenity_code(amenity_en):
    """amenity_en hiển thị -> amenity snake_case (U-1: B + bỏ dấu).
    "Spa & Wellness" -> "spa_wellness", "servesWine" -> "serves_wine", "Pet Café" -> "pet_cafe"."""
    s = unicodedata.normalize("NFKD", (amenity_en or "").strip())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = AMENITY_CAMEL_RE.sub("_", s).lower()
    return AMENITY_CODE_RE.sub("_", s).strip("_")


def amenity_seed_rows(rows):
    """SEED_ROWS 7 trường -> 8 trường theo thứ tự cột bảng:
    (source, sector, group, raw, amenity, amenity_en, amenity_vi, service_flags)."""
    return [(s, sec, g, raw, amenity_code(en), en, vi, flags) for s, sec, g, raw, en, vi, flags in rows]
```

In `validate_seed`:
- Rename the unpacked 5th field from `amenity` to `amenity_en`.
- Keep the existing checks.
- Append:

```python
    coded = amenity_seed_rows(rows)
    bad = [row[5] for row in coded if not AMENITY_CODE_SHAPE.fullmatch(row[4])]
    if bad:
        raise ValueError(f"amenity snake_case sai dạng: {bad[:5]}")
    code_keys = [row[:5] for row in coded]
    if len(code_keys) != len(set(code_keys)):
        raise ValueError("ref_dictionary_amenities: trùng khoá 5 cột sau snake_case")
```

### `c1setupplan` — row 3

- `SEED_SCHEMA = "source_name string, business_sector string, amenity_group string, amenity_raw string, amenity string, amenity_en string, amenity_vi string, service_flags string"`.
- `seed_df = spark.createDataFrame(amenity_seed_rows(SEED_ROWS), SEED_SCHEMA)`.
- Compute `ref_has_amenity_en` and `slv_has_amenity_en` from the table columns. Each is False when its table is absent. Add both to the print and to the PLAN exit JSON.

### `c1setupddl` — row 4

Place this before the existing CREATE statements:

```python
def _cols(fq):
    return [f.name.lower() for f in spark.table(fq).schema.fields] if table_exists(fq) else None


ref_cols = _cols(REF_FQ)
if ref_cols is not None and "amenity_en" not in ref_cols:
    raise ConfigError(f"{REF_FQ} chưa có amenity_en: seed insert-only và khoá amenity đổi, "
                      "DROP bảng rồi chạy lại NB_SETUP_POI_AMENITY")
slv_cols = _cols(AMENITY_FQ)
if slv_cols is not None and "amenity_en" not in slv_cols:
    spark.sql(f"ALTER TABLE {AMENITY_FQ} ADD COLUMNS (amenity_en STRING AFTER amenity)")
```

- `ref` CREATE: add `amenity_en STRING NOT NULL,` after `amenity`.
- slv CREATE: add `amenity_en STRING,` after `amenity`.
- `EXPECTED`: add `("amenity_en", "string", False)` after `amenity` for `ref`, and `("amenity_en", "string", True)` for slv. Use the tuple form the cell already uses for nullability.

### `c1setupmerge` — row 5

- Add `amenity_en` to the INSERT column list and `s.amenity_en` to VALUES.
- In the DRIFT `WHERE NOT (...)`, add `t.amenity_en <=> s.amenity_en AND`.
- Do not add `WHEN MATCHED`.

### `NB_SETUP_INITIAL_DDL` — rows 2, 6, 7, 8

- `init_tables` `TABLE_SPECS`:
  - `ref`: add `('amenity_en', 'STRING', 'NOT NULL')` after `amenity`. Follow the existing constraint encoding of `amenity` in that spec.
  - slv and gold: add `('amenity_en', 'STRING', None)`.
- `init_seed_amenity`: the same block as `c1setupseed`. Keep `AMENITY_ROWS = list(SEED_ROWS)`.
- `init_plan` `_v_setup_amenities`: `createDataFrame(amenity_seed_rows(AMENITY_ROWS), "... amenity STRING, amenity_en STRING, amenity_vi STRING, service_flags STRING")`.
- `init_seed_write`:
  - `_merge_amenities` INSERT: add `amenity_en`.
  - Drift SQL: add `t.amenity_en <=> s.amenity_en`.
  - Key lists are unchanged.

### `NB_SLV_POI_AMENITY` `d1amenbuild` — row 9

```python
COND_SCHEMA = ("business_sector string, amenity_group string, amenity_raw string, amenity string, "
               "amenity_en string, amenity_vi string, service_flags string, _kind string, _path string, _v string")
OUT_COLS = ("poi_id", "business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_en", "amenity_vi",
            "service_flags")
```

In `build`:
1. After the `service_flags` dtype check, add: `if dict(d.dtypes).get("amenity_en") != "string": raise ConfigError("ref_dictionary_amenities thiếu cột amenity_en STRING: DROP và chạy lại NB_SETUP_POI_AMENITY")`.
2. The select becomes `("business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_en", "amenity_vi", "service_flags")`.
3. After collecting `rows`, compute `blank = sum(not (r[3] or "").strip() or not (r[4] or "").strip() for r in rows)`. If `blank > 0`, raise `QualityGateError` before `match_conditions`. Add the metric `dict_amenity_en_blank=blank`.
4. In `conditions_service_flags`, change `c[5]` to `c[-4]`.

`# BEGIN_AMENITY_MATCH` stays unchanged. `match_conditions` passes through the tuple fields it gets from the select.

### Gold — rows 10, 11

- `srvamenitybuild`: `OUT_COLS` equals the slv `OUT_COLS`.
- `amenddlpy` `AMENITY_COLS`: add `('amenity_en', 'STRING')` after `amenity`.
- `amenddlmd`: add the line "20261109: thêm amenity_en; bảng cũ phải DROP trước khi chạy cell này".

### PostgreSQL — row 12

`CREATE TABLE apps.srv_poi_amenity`: add `amenity_en text,` after `amenity text,`. The PK is unchanged.

### Java — rows 15–18

- `SrvPoiAmenity`: add `@Column(name = "amenity_en") private String amenityEn;` after `amenity`, with a getter that follows the existing style.
- `PoiAmenityId`, `SrvPoiAmenityRepository`: no change.
- `PoiAmenityGroupResponse`:

```java
@JsonInclude(JsonInclude.Include.ALWAYS)
public record PoiAmenityGroupResponse(
        @JsonProperty("amenity_group") String amenityGroup,
        @JsonProperty("items") List<Item> items) {
    @JsonInclude(JsonInclude.Include.ALWAYS)
    public record Item(
            @JsonProperty("amenity_code") String amenityCode,
            @JsonProperty("amenity_label_en") String amenityLabelEn,
            @JsonProperty("amenity_label_vi") String amenityLabelVi,
            @JsonProperty("service_flags") String serviceFlags) {}
}
```

Keep the `@Schema` descriptions, with snake_case examples.

- `PoiService`:
  1. Delete `AMENITY_GROUP_LABELS_VI`, `AMENITY_GROUP_LABELS_EN`, `getAmenities(String, String)`, and the `GENERAL` and `amenity_raw` fallbacks. `amenity_group` is a PK column, so it is never null.
  2. Add a single `@Transactional(readOnly = true) List<PoiAmenityGroupResponse> getAmenities(String poiId)` that does the following:
     1. `validatePoiExists`.
     2. `findByPoiIdAndDeletedAtIsNull`.
     3. Apply the existing `json_type` filter.
     4. Sort as described in "Ordering".
     5. Group into a `LinkedHashMap`.
     6. Map each row to `new Item(a.getAmenity(), a.getAmenityEn(), a.getAmenityVi(), a.getServiceFlags())`.
- `PoiController.getAmenities`:
  - Keep only `@PathVariable("poi_id") String poiId`.
  - Call `poiService.getAmenities(poiId)`.
  - Keep the same message and path.
  - Keep the `LanguageResolver` field if other endpoints use it.

### Documentation — rows 22–24

- `mapping_gld_srv_poi_amenity.md`:
  - §0: `OUT_COLS` and the DDL with `amenity_en`, plus RULE-U1 as `amenity = amenity_code(amenity_en)`.
  - §1: the gold row for `amenity_en`, and the JSON-to-column table from I-10.
  - Migration note: DROP `ref`, gold, and PostgreSQL; ALTER slv.
- `01_DATA_MODEL.md`: rows `ref_dictionary_amenities` and N7 `slv_poi_amenity` get `amenity_en` and the snake_case note.
- `api-mapping/amenities.md` (only if S-1 adds it):
  - Remove request rows `Accept-Language` and `lang`, and response rows `data[].amenity_vi` and `amenity_label`.
  - Add `amenity_label_en`/`amenity_label_vi`.
  - Change `amenity_code` to read `amenity` with no fallback.
  - Remove the `GENERAL` fallback.
  - Use the D-01 sample.

## Verification

### Local, Main runs

| ID | Test | File |
|---|---|---|
| T-1 | `test_amenity_code_rule_cases`. Pairs: `Free Street Parking`→`free_street_parking`, `24-hour Front Desk`→`24_hour_front_desk`, `Spa & Wellness`→`spa_wellness`, `Private Room (VIP)`→`private_room_vip`, `Yakiniku / Teppanyaki`→`yakiniku_teppanyaki`, `Pet Café`→`pet_cafe`, `Pet Café` (NFD)→`pet_cafe`, `servesWine`→`serves_wine`, `servesVegetarianFood`→`serves_vegetarian_food`, `pureServiceAreaBusiness`→`pure_service_area_business`, `acceptsNfc`→`accepts_nfc`, `EV Charging Station`→`ev_charging_station`, `Free Wi-Fi`→`free_wi_fi`, `E-Wallet`→`e_wallet`, `takeout`→`takeout`, `Good for Children`→`good_for_children`, `Family Friendly`→`family_friendly`. Edge cases: `""`→`""`, `None`→`""`. Idempotence holds for every seed row. | `tests/test_poi_amenity_contract.py` |
| T-2 | `test_seed_rows_with_code_shape`. There are 175 eight-tuples. `row[5] == SEED_ROWS[i][4]` and `row[4] == amenity_code(row[5])`. Every code fully matches `AMENITY_CODE_SHAPE`. The 5-column key is unique. `validate_seed` passes. `validate_seed` raises on a synthetic row with `amenity_en="Đỗ"` (shape) and on a duplicated row (key). | same |
| T-3 | `test_match_conditions_carries_amenity_en`. Build google 7-tuples from `amenity_seed_rows` without `source`. Then `c[4]` is `amenity_en` and `c[-4]` is `service_flags`. | same |
| T-4 | Update `test_amenity_node_contract`: `OUT_COLS` has `amenity_en` right after `amenity`; `"service_flags string, _kind"` is present; the build contains `c[-4] is not None`; the `amenity_en STRING` guard text and `dict_amenity_en_blank=` are present. Update `test_setup_contract`: `ADD COLUMNS (amenity_en STRING AFTER amenity)` is in `c1setupddl`, `amenity_en` is in the MERGE INSERT, and `WHEN MATCHED` is absent. | same |
| T-5 | `test_amenity_en_order_across_layers`. `amenity_en` sits right after `amenity` in slv `TABLE_SPECS`, gold `TABLE_SPECS`, `AMENITY_COLS`, the PostgreSQL DDL, and the entity field order. | `tests/test_srv_poi_serving_contract.py` |
| T-5b | Add `("amenity_en","STRING",None)` after `amenity` in the `AMENITY_COLS` constant. `test_amenity_untouched` stays green. | `tests/test_poi_media_amenity_contract.py` |
| T-6 | Replace `shouldReturnGroupedAmenitiesSuccessfully` with `shouldMapAmenityColumnsToD01Fields` (the fixture has distinct `amenity_vi` and `service_flags`, and the test asserts that `service_flags` comes from the column), `shouldOrderAmenityGroupsAndItemsDeterministically`, and `shouldFilterJsonTypeAmenityRows`. Keep `shouldReturnEmptyListWhenPoiHasNoAmenities` and `shouldThrowWhenPoiNotFoundInAmenities` with the 1-arg call. | `PoiServiceTest.java` |
| T-7 | `shouldReturnAmenitiesSuccessfully` asserts the D-01 JSON paths and that `$.data[0].amenity_vi` and `$.data[0].items[0].amenity_label` do not exist. Replace `shouldSupportAmenitiesMultiLanguage` with `shouldIgnoreLangQueryAndAcceptLanguageForAmenities` (`?lang=en` plus the header returns 200, and `verify(poiService).getAmenities("poi_01")`). Update the empty and 404 tests to the 1-arg call. | `PoiControllerIntegrationTest.java` |

These tests must stay green without edits: `test_seed_matches_mapping_file`, `test_amenity_keys_cases`, `test_amenity_ddl_matches_node`, `test_gold_and_pg_columns_and_types_match`, `test_entities_match_gold_columns_types_and_keys`, `tests/test_initial_ddl_contract.py`, and `DataServingApplicationTests`.

Commands:
- `python -m pytest tests/test_poi_amenity_contract.py tests/test_srv_poi_serving_contract.py tests/test_poi_media_amenity_contract.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py tests/test_enr_poi_contract.py -q`
- `python -m pytest tests -q`
- `cd services/data-serving-service && mvnw.cmd -q -B test`

### Runtime proof (user runs; queries go into the runbook)

P-1, `ref`:
- `count(*) = 175`.
- `count(DISTINCT source_name, business_sector, amenity_group, amenity_raw, amenity) = 175`.
- The setup prints `stale=0 drift=0`.
- The rule check below returns 0. It is valid because the seed's only non-ASCII letter is `é`, as T-2 shows.

```sql
SELECT count(*) FROM lh_vv_silver.dbo.ref_dictionary_amenities
WHERE amenity <> regexp_replace(
        regexp_replace(lower(regexp_replace(translate(amenity_en, 'é', 'e'), '([a-z])([A-Z])', '$1_$2')),
                       '[^a-z0-9]+', '_'),
        '^_+|_+$', '')
```

P-2: `DESCRIBE lh_vv_silver.dbo.slv_poi_amenity` shows `amenity_en` between `amenity` and `amenity_vi`. The setup `EXPECTED` check passed.

P-3, slv:
- `count(*) WHERE deleted_at IS NULL AND (amenity IS NULL OR amenity_en IS NULL)` is 0.
- The metric `dict_amenity_en_blank=0`.
- The query below returns 0:

```sql
SELECT count(*) FROM lh_vv_silver.dbo.slv_poi_amenity s
LEFT ANTI JOIN lh_vv_silver.dbo.ref_dictionary_amenities r
  ON r.source_name = 'google' AND r.is_active AND r.business_sector = s.business_sector
 AND r.amenity_group = s.amenity_group AND r.amenity = s.amenity AND r.amenity_en = s.amenity_en
WHERE s.deleted_at IS NULL
```

P-4, slv grain: `count(*) = count(DISTINCT poi_id, business_sector, amenity_group, amenity_raw)`.

P-5, gold vs slv: compare `OUT_COLS` plus `deleted_at`. `EXCEPT` in both directions returns 0 rows. The gold `DESCRIBE` matches `AMENITY_COLS`.

P-6, PostgreSQL:
- The row count equals the gold row count.
- `count(*) WHERE deleted_at IS NULL AND amenity_en IS NULL` is 0.
- `count(*) WHERE amenity !~ '^[a-z0-9]+(_[a-z0-9]+)*$'` is 0.

P-7, API: `curl /api/v1/pois/{poi_id}/amenities` for a POI with amenities.
- The response matches the D-01 shape.
- `amenity_label_vi` differs from `service_flags` where the data differs.
- The same call with `?lang=en` and with `Accept-Language: en` returns identical `data`.
- An unknown POI returns 404.
