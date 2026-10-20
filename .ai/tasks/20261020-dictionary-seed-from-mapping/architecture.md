RESULT: PASS

## Main brief

### Decision
Hard-code 11-field place-type `SEED_ROWS`. Each row is (source, place_type, sector, category, category_vi, category_group, range_low_min, range_high_min, avg_range_min, candidate_best_time_code, canonical_candidate). Add 31 new google rows (D-04) and 17 amenity rows `other/other` (D-05).
Remove `category_group()` and `with_category_group()`. Add five nullable columns after `category_group`. Mirror everything in `NB_SETUP_INITIAL_DDL`. Add a new `NB_CREATE_DDL` patch cell that declares the columns only.
DEV rebuild for both tables: back up with CTAS, `DROP`, re-init with the owner setup notebook, count. The user runs it.
Expected counts: place type 387 (328 google / 59 partner); amenities 175 (101 / 74).

### Invariants Main must preserve
- Every place-type seed row has 11 fields. `category_group` is in `CATEGORY_GROUP_VALUES`. The three range fields are `int` with low ≤ avg ≤ high. `BEST_TIME_CANONICAL[code] == canonical`, including the U+2013 dash.
- No `def category_group` or `with_category_group` anywhere in `NB_SETUP_POI_ENTITY` or `NB_SETUP_INITIAL_DDL`. The old `NB_CREATE_DDL` cell `nonenrpy` stays unchanged.
- Seed blocks are byte-identical between `NB_SETUP_POI_*` and `NB_SETUP_INITIAL_DDL`.
- The column list is identical, in order and type, in the `a1setupddl` CREATE, `EXPECTED`, `TABLE_SPECS`, and the patch `NEW_COLS`. New columns are nullable.
- Seed MERGEs stay insert-only (no `WHEN MATCHED`). `p_apply` defaults to `"false"`.
- `NB_SETUP_POI_ENTITY` apply raises when the target has rows with NULL `category_group` or NULL estimate columns, or still has the old schema.
- Existing seed rows keep their order and first five fields. New rows are appended in doc order (§1.9.1, then §1.9.2; §2.5).
- `mapping_place_type.md` L186–L270 and `mapping_amenities.md` §2.5 stay byte-identical. §1.8 lists exactly the current `CATEGORY_GROUPS` tokens.
- Matching is exact strings only, after rewriting Latin spaces to `_` once (`theme` and `theme_park` are both new rows; `ferry_terminal` and `hindu_temple` get no special values).
- Do not stage the user's deletion of `Mapping_POI_Service_Data.md`.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1 | docs/context/3p-google/mapping_place_type.md | `# **1.8. Category Group**` | Add a Google group→tokens table (`CATEGORY_GROUPS` order), the line "not listed → Other", and a Partner enum→group table using the D-03 values | Tests 13 and 14 pass; L186–L270 unchanged |
| 2 | notebooks/NB_SETUP_POI_ENTITY.ipynb | `a1setupseed` | 11-field `SEED_ROWS` plus 31 appended rows. Replace `CATEGORY_GROUPS`, `category_group` and `with_category_group` with the block in doc §Implementation plan › "Code: seed validation block" | `validate_seed(SEED_ROWS)` passes; oracle tests pass |
| 3 | notebooks/NB_SETUP_POI_ENTITY.ipynb | `a1setupplan` | Widen `SEED_SCHEMA`; drop `rows6`; add the `unseeded` guard, the PLAN JSON key, and the apply raise (doc "Code: a1setupplan changes") | Plan JSON has `unseeded_rows` |
| 4 | notebooks/NB_SETUP_POI_ENTITY.ipynb | `a1setupddl` | Five columns in CREATE and `EXPECTED`; new ConfigError text (doc "DDL, MERGE and drift text") | `test_columns_match_sources` passes |
| 5 | notebooks/NB_SETUP_POI_ENTITY.ipynb | `a1setupmerge` | INSERT columns/values plus five `<=>` checks in `DRIFT` | `test_setup_contract` passes |
| 6 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupseed` | Add `other` to `SEED_SECTORS` and `SEED_GROUPS`; append the comment and 17 rows (doc "Amenity seed") | `test_seed_counts` gives 175 |
| 7 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` | Five entries in the `ref_dictionary_place_type` `TABLE_SPECS` | `test_columns_match_sources` passes |
| 8 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_place_type` | Byte-copy of row 2's seed block; tail becomes `validate_seed(SEED_ROWS)` + `PLACE_TYPE_ROWS = list(SEED_ROWS)` | `test_ref_seed_blocks_identical` passes |
| 9 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_amenity` | Byte-copy of row 6's seed block | Same test |
| 10 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_plan` | `_v_setup_place_type` schema plus five columns | Plan cell runs in tests that exec it |
| 11 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_write` `_merge_place_type` and place-type drift SQL | INSERT plus five columns; drift adds `category_group` and the five columns | `test_no_destructive_sql` still passes |
| 12 | notebooks/NB_CREATE_DDL.ipynb | new trailing cells `dictseedmd`, `dictseedpy` | Markdown `[THÊM 20/10] 20261020-dictionary-seed-from-mapping` plus the cell in doc "Code: NB_CREATE_DDL patch". Do not edit `nonenrpy`. | Test 9 passes |
| 13 | tests/test_poi_entity_contract.py | `parse_mapping`, `test_seed_matches_mapping_file`, `test_seed_keys_unique_and_tokens_valid`, `test_seed_counts`, `test_setup_contract`, `test_create_ddl_patch`; replace `test_category_groups_seed` and `test_partner_group_resolution_on_seed` | See Tests | All pass |
| 14 | tests/test_poi_amenity_contract.py | `parse_mapping`, `test_seed_matches_mapping_file`, `test_seed_counts`, `test_seed_sectors_groups`; new tests | See Tests | All pass |
| 15 | tests/test_initial_ddl_contract.py (after Stop 0) | `test_ref_seed_blocks_identical` L406 | Assert `PLACE_TYPE_ROWS = list(SEED_ROWS)` | Passes |
| 16 | docs/context/01_DATA_MODEL.md (after Stop 0) | rows L343–L344 | New columns, counts 387 (328/59) and 175 (101/74), hard-coded per-row rule, rebuild runbook; remove the "Backfill chỉ dòng đang NULL" sentence | Text matches |
| 17 | .ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md | whole file | Copy runbook R0–R12 and RB from the doc | User can run it as written |

### Order and stop points
1. **STOP 0 (state/user):** add `tests/test_initial_ddl_contract.py` (required: line 406 pins `with_category_group`) and `docs/context/01_DATA_MODEL.md` to `scope.files`.
2. **STOP 1 (user decision D-07):** `pagoda`, `night_market`, `theme_park` are both new rows and §1.8 tokens. Ask whether §1.8 wins (recommended; `theme_park` then gets 180/360/270) or D-04 `Other` wins (`theme_park` gets 60/90/75). Record the answer in `decision.md` before writing these three rows.
3. Do row 1 (docs §1.8).
4. Do rows 2–6, then byte-copy rows 8–9, then rows 7, 10–12.
5. Do rows 13–15 (tests).
6. **STOP 2 (user decision, only if triggered):** stop if `test_partner_category_group_from_mapping_row` finds a partner enum with ≥2 distinct non-Other groups (D-03 does not cover it). Also stop if `test_partner_group_matches_node_rule` shows the row-based group differs from the node's category-based group for any partner. Report the enums; do not choose.
7. Do row 16, then local verification (below).
8. **STOP 3 (evidence):** specialist review (`sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`), then `risk-gate`.
9. **STOP 4 (runtime evidence):** the user runs the runbook on Fabric DEV (R3 is a hard stop before any DROP). Main records the outputs and does not set `gates.runtime`.

### Tests and verification
New or rewritten tests in `tests/test_poi_entity_contract.py`:
- `parse_mapping`: use `SECTOR.get(...)`; for a section not in `SECTOR` (1.8, 1.9), set `sector=None, cols=None` and skip its rows.
- `test_seed_matches_mapping_file`: `[r[:5] for r in SEED_ROWS[:356]] == parse_mapping(...)[0]`. Also `SEED_ROWS[356:]` keys equal the 31 tokens listed in the doc (Grain and keys), in order, each with `('other','other','other')`.
- `test_seed_keys_unique_and_tokens_valid`: allow only `TOKEN_KEEP` (`suối`, `thác`) outside `^[a-z0-9_]+$`.
- `test_seed_counts`: google 328, partner 59.
- `test_category_group_from_section_1_8`: parse the §1.8 Google table. Its tokens equal the old `CATEGORY_GROUPS` literal. Every google row's group equals the lookup, or `Other`. The three D-07 tokens follow the recorded decision.
- `test_partner_category_group_from_mapping_row`: D-03 oracle over §1.1–§1.7 rows. Assert no partner has ≥2 non-Other groups. Pinned values: Hotel→Lodging, Homestay→Lodging, Café→`Light Snacks / Cafe`, Vietnamese→Other, `Car with Driver`→Other. The §1.8 Partner table equals the seed.
- `test_partner_group_matches_node_rule`: the row-based group equals the old category-based resolution (steps 1 and 2 over google rows) for every partner.
- `test_estimates_from_section_1_9`: oracle for L193–L210 and L218–L242 (skip priority 10 and Default; lowest priority wins; exact match only). Every row equals it.
- `test_estimate_spot_values`: literal 11-tuples for `beach`, `market`, `national_park`, `water_park`, `suối`, `cable_car`, `ferry_terminal`, `hindu_temple`, `hotel`, and partner `Café`.
- `test_validate_seed_rejects_bad_rows`: each of these raises: bad label, low>high, code/canonical mismatch, a 10-field row, a `None` range.
- `test_no_category_group_function`: no `def category_group` or `with_category_group` in the `NB_SETUP_POI_ENTITY` or `NB_SETUP_INITIAL_DDL` code.
- `test_section_1_9_preserved`: the 1.9 / 1.9.1 / 1.9.2 / 1.9.3 headings and the `deterministic_cost_vnd = ROUND((price_min + price_max) / 2)` line are present.
- `test_setup_contract`: the DDL has the five columns and types; the plan has `unseeded_rows` and the raise.
- `test_create_ddl_patch`: the last two cells are `dictseedmd` and `dictseedpy`. The patch has `ADD COLUMNS` guarded by `missing`, and no `UPDATE`/`CATEGORY_GROUPS`. `NEW_COLS` equals the tail of `EXPECTED`. `nonenrpy` still exists.

Changed and new tests in `tests/test_poi_amenity_contract.py`:
- `parse_mapping` skips 2.5.
- `test_seed_matches_mapping_file`: `SEED_ROWS == _expand(parsed) + rows_2_5`. The 2.5 oracle uses the Food/service, Suitability, Payment and Accessibility rows. A token is "existing" if it, or (Accessibility only) `accessibilityOptions.`+token, is a google `amenity_raw`; otherwise it becomes a new other/other row.
- `test_seed_counts`: 175 / 74 / 101; `("other","google")` = 17.
- `test_seed_sectors_groups`: includes `other`; `other` rows use only group `other`.
- New `test_section_2_5_rows`: the exact list of 17; no `parkingOptions.*`, Derived, or short wheelchair rows.
- New `test_section_2_5_rows_inert`: `resolve_condition('other','other',t) is None`, and `match_coverage` is still `([], [])`.

Commands:
```
python -m pytest tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py -q
python -m pytest -q
python scripts/vv.py verify
```

### Read only if needed
- `Model-design reconciliation` → STOP 1, rows 2, 13
- `Invariants` → all rows
- `Grain and keys` → rows 2, 6, 13, 14
- `Value rules (seed authoring; tests re-derive them)` → rows 1, 2, 13
- `Implementation plan` › `Code: seed validation block` → rows 2, 8
- `Implementation plan` › `Code: a1setupplan changes` → row 3
- `Implementation plan` › `Code: NB_CREATE_DDL patch` → row 12
- `Implementation plan` › `DDL, MERGE and drift text` → rows 4, 5, 7, 10, 11
- `Implementation plan` › `Amenity seed` → rows 6, 9
- `Implementation plan` › `Docs` → rows 1, 16
- `Implementation plan` › `Runtime runbook` → row 17, STOP 4
- `Partial failure`, `Rollback and forward recovery`, `Concurrency` → row 17
- `Alternatives` → reviewer questions on drop vs. ALTER

# Architecture: 20261020-dictionary-seed-from-mapping

Inputs: `request.md`, `decision.md` D-01 to D-06, and `model-design.md` (headings `Entities and grain`, `Keys`, `Columns`, `Conflicts and questions`). The source was read at: `NB_SETUP_POI_ENTITY` (`a1setupseed`, `a1setupplan`, `a1setupddl`, `a1setupmerge`, `a1setupexit`), `NB_SETUP_POI_AMENITY` (`c1setupseed` to `c1setupmerge`), `NB_SETUP_INITIAL_DDL` (`init_tables`, `init_seed_*`, `init_plan`, `init_seed_write`, `init_verify`), `NB_CREATE_DDL` (`nonenrpy`), the readers `NB_SLV_POI_ENTITY_NON_ENRICH` (`b1entitybuild`) and `NB_SLV_POI_AMENITY` (`BEGIN_AMENITY_MATCH`, `d1amenbuild`), `edge_status` in `NB_LIB_TRANSFORM_SLV_GLD`, the three contract tests, `02_NAMING_CONVENTION.md` §2.1, and `01_DATA_MODEL.md` L343–L344.

The verdict is PASS, with two stop points before implementation:
- **Stop 0:** `scope.files` must be extended.
- **Stop 1:** user decision D-07 on three tokens.

Neither stop changes the shape of the design.

## Scope

- `ref_dictionary_place_type` gets five nullable columns, named and typed per D-06: `range_low_min INT`, `range_high_min INT`, `avg_range_min INT`, `candidate_best_time_code STRING`, `canonical_candidate STRING`. They are appended after `category_group`.
- Every place-type `SEED_ROWS` entry becomes an 11-field literal that carries `category_group` plus the five values. There are 31 new `google` rows (D-04).
- `category_group` and `with_category_group` are removed from the seed block. `CATEGORY_GROUPS` is replaced by a validation-only label list.
- `ref_dictionary_amenities`: no column change. The 17 D-05 rows are appended as (`google`, `other`, `other`, raw, raw, raw), and `other` is added to the amenity `SEED_SECTORS` and `SEED_GROUPS`.
- Mirrors:
  - `NB_SETUP_INITIAL_DDL` gets the byte-identical seed blocks, `TABLE_SPECS`, the view schema, the insert columns and the drift SQL.
  - `NB_CREATE_DDL` gets a new trailing patch cell `[THÊM 20/10]` that declares the columns only.
- Docs:
  - `mapping_place_type.md` §1.8 gets two tables: Google tokens → group, and Partner enum → group.
  - §1.9 to §1.9.3 and `mapping_amenities.md` §2.5 stay byte-identical.
- Tests: the doc→seed oracle, pinned spot values, and the new counts.
- The runtime runbook: back up, drop, re-init, count, and roll back. The user runs it on Fabric DEV.

## Non-goals

- `NB_SLV_POI_ENTITY_NON_ENRICH` keeps deriving the partner `category_group` from Google rows grouped by `business_category`. It does not read partner rows' `category_group`, and this task does not change that.
- `NB_SLV_POI_AMENITY` `FLAG_MATCH` is not extended. The 17 new rows resolve to `None` in `resolve_condition` and produce no `slv_poi_amenity` output. This is intended and inert.
- No downstream consumer of the five estimate columns. Section 1.9.3 does not become a seed row, and there is no `priority` column.
- The 1.7 tokens, `Car with Driver` / `Campervan Rental` Google types, and the 1.5 label winners stay as they are (D-01).
- No `OUTDOOR_TYPES` / `dry_season` (D-04). No new `parkingOptions.*`, Derived, or coworking rows (D-05).
- The old `NB_CREATE_DDL` cell `nonenrpy` stays unchanged as history (`02_NAMING_CONVENTION.md` §2.1 rule 4).
- The working-tree deletion of `docs/context/3p-google/Mapping_POI_Service_Data.md` is the user's change. Do not stage it with this task.

## Model-design reconciliation

Grain and keys are unchanged; see `model-design.md` `Entities and grain` and `Keys`. The open items in `Conflicts and questions` are closed by the ledger:

| model-design item | Closed by | Effect here |
|---|---|---|
| 1 (new place types vs Constraints) | D-04 ("thay câu Constraints") | 31 new `google` rows |
| 2, 3 (names, types, parentheses) | D-06 | `default_range(min)` becomes `range_low_min` + `range_high_min` INT. `avg_range(min)` becomes `avg_range_min` INT. Thousands separators are stripped. |
| 4 (coverage, precedence 1.9.1) | D-04 | Every row gets the group default from L193–L201. An exact `place_type` in L205–L210 overrides it. |
| 5 (priority, default 1.9.2) | D-04 | The lowest priority wins. No match gives `all` / `all_year`. Partner rows match only by exact string, so in practice they get `all`. |
| 6 (partner with none or ≥2 groups) | D-03 | None gives `Other`. ≥2 is a stop point (the test oracle asserts there are none). |
| 7 (short wheelchair names) | D-05 | No row and no alias. They map to the existing prefixed rows. |
| 8 (`is_active`) | D-04, D-05 | `true` through the existing MERGE `VALUES` |
| 9 (counts) | this design | Place type: 387 = 328 google + 59 partner. Amenities: 175 = 101 google + 74 partner. |

**Open conflict (D-07, user decision).** Three tokens hit two rules at once:
- They are new rows, and D-04 plus doc L203/L216 say new rows get `category_group = Other`.
- They are also listed in §1.8 (`CATEGORY_GROUPS`), and request Constraints plus D-03 say a Google `place_type` takes its §1.8 group.

| token | §1.8 group | value if §1.8 wins | value if D-04 `Other` wins |
|---|---|---|---|
| `pagoda` | Light Sightseeing / Culture & Nature | ranges 60/120/90 (special row, same either way) | same ranges, group `Other` |
| `night_market` | Shopping & Nightlife | ranges 90/150/120 (special row, same either way) | same ranges, group `Other` |
| `theme_park` | Heavy Entertainment | 180/360/270 | 60/90/75 |

Recommendation: §1.8 wins. D-03 already states that only tokens not in §1.8 are `Other`, and with that choice §1.8 and the seed never disagree. This is not a rule written in the ledger, so Main must record D-07 before writing these three rows. Row counts do not depend on D-07.

## Invariants

1. **Keys.** (`source_name`, `place_type`) is unique in `SEED_ROWS` and in the table. The amenity 5-column key is unique, and 4-column duplicates exist only in `AMENITY_SHARED_RAW`.
2. **Place-type row shape.** Every place-type seed row has 11 fields:
   - `category_group` is one of the 7 labels.
   - `range_low_min`, `range_high_min` and `avg_range_min` are Python `int`, with low ≤ avg ≤ high.
   - `canonical_candidate == BEST_TIME_CANONICAL[candidate_best_time_code]`.
   - No field is `None`, except the existing `business_category` / `business_category_vi` `None` values on rows such as `Car with Driver` and the 1.7 rows.
3. **No derivation in code.** No code in `NB_SETUP_POI_ENTITY` or `NB_SETUP_INITIAL_DDL` assigns `category_group` or estimate values: no `def category_group`, and no `with_category_group`. The only allowed occurrence is the historical `NB_CREATE_DDL` cell `nonenrpy`.
4. **Mirrored seed blocks.** `BEGIN_PLACE_TYPE_SEED…END` and `BEGIN_AMENITY_SEED…END` are byte-identical between `NB_SETUP_POI_*` and `NB_SETUP_INITIAL_DDL`.
5. **One column list.** The `ref_dictionary_place_type` column list (names, types, order, nullability) is identical in:
   - the `a1setupddl` CREATE,
   - `a1setupddl` `EXPECTED`,
   - `init_tables` `TABLE_SPECS`,
   - and, for the five new columns, the `NB_CREATE_DDL` patch `NEW_COLS`.

   The new columns are nullable (naming rule 5).
6. **Insert-only seed.** Seed MERGEs stay insert-only. No `WHEN MATCHED` appears in `a1setupmerge`, `c1setupmerge` or `init_seed_write`.
7. **Plan before write.** `p_apply` defaults to `"false"`, and the plan exits before any write.
8. **Apply refuses unseeded rows.** `NB_SETUP_POI_ENTITY` apply refuses (raises `ConfigError` before any write) when the target table has a row with NULL in `category_group` or in any of the five columns. This blocks the silent state "schema patched, values missing".
9. **Docs.**
   - §1.9, §1.9.1, §1.9.2 and §1.9.3 (current L186–L270) and `mapping_amenities.md` §2.5 (L142–L155) stay byte-identical.
   - §1.8 lists exactly the current `CATEGORY_GROUPS` tokens in their current order, plus the Partner table.
10. **Seed equals docs.** Seed order:
    - Existing rows keep their order and their first five fields. Existing place-type rows equal `parse_mapping` §1.1–§1.7.
    - The 31 new place-type rows are appended in order of first appearance in §1.9.1 and then §1.9.2.
    - The 17 amenity rows are appended in §2.5 order.

## State ownership

| State | Owner (writes) | Mirrors / patches | Readers |
|---|---|---|---|
| `ref_dictionary_place_type` DDL + seed | `NB_SETUP_POI_ENTITY` | `NB_SETUP_INITIAL_DDL` (fresh env), `NB_CREATE_DDL` `[THÊM 20/10]` (columns only) | `NB_SLV_POI_ENTITY_NON_ENRICH` via edge `ref_dictionary_place_type → slv_poi_entity_non_enrich` (RECOMPUTE) |
| `ref_dictionary_amenities` seed | `NB_SETUP_POI_AMENITY` | `NB_SETUP_INITIAL_DDL` | `NB_SLV_POI_AMENITY` via edge `ref_dictionary_amenities → slv_poi_amenity` |
| Truth for values | `mapping_place_type.md` §1.8, §1.9.1, §1.9.2 and `mapping_amenities.md` §2.5 (human) | hard-coded `SEED_ROWS` | tests (oracle) |
| Backup tables `*_bak_20261020` | user, during the runbook | none | user only, for rollback |

## Grain and keys

Unchanged. See `model-design.md` `Entities and grain` and `Keys`. New key values:

- **31 place types.** Each is (`google`, token), with `business_sector` / `business_category` / `business_category_vi` = `other`.
  - From §1.9.1: `cable_car`, `safari`, `theme`, `vinwonders`, `night_market`, `pagoda`, `temple`, `prison`, `snorkel`, `island`, `boat`.
  - From §1.9.2: `snorkeling`, `diving`, `scuba`, `canoe`, `ferry`, `sailing`, `sunset`, `coast`, `coastal`, `stream`, `suối`, `thác`, `forest`, `hiking`, `trekking`, `trail`, `shopping`, `mall`, `wellness`, `theme_park`.
  - A grep confirmed that none of them exists today.
  - `theme` and `theme_park` are both new. D-04 matches exact strings only and allows no prefix extension.
- **17 amenities.** Each is (`google`, `other`, `other`, raw, raw), using the D-05 list. A grep confirmed that none exists.

## Value rules (seed authoring; tests re-derive them)

- **`category_group`**
  - Google rows: the §1.8 token → group lookup. Tokens not listed get `Other`. For new rows, see D-07.
  - Partner rows: take the doc table row(s) where the partner enum appears and collect the §1.8 groups of that row's Google tokens. Exactly one non-`Other` group gives that group. Zero gives `Other`. Two or more is a STOP. D-02 makes Homestay `Lodging`.
  - Expected spot values: Hotel → Lodging, Homestay → Lodging, Café → Light Snacks / Cafe, Vietnamese → Other, Car with Driver → Other.
- **Ranges.** The group default comes from L193–L201, with separators stripped:

  | group | low | high | avg |
  |---|---|---|---|
  | Lodging | 1200 | 1200 | 1200 |
  | Main Meals | 60 | 90 | 75 |
  | Light Snacks / Cafe | 45 | 60 | 60 |
  | Heavy Entertainment | 180 | 360 | 270 |
  | Light Sightseeing / Culture & Nature | 60 | 120 | 90 |
  | Shopping & Nightlife | 60 | 180 | 120 |
  | Other | 60 | 90 | 75 |

  An exact `place_type` listed in L207–L210 overrides the default, after rewriting Latin spaces to `_` once:

  | tokens | low | high | avg |
  |---|---|---|---|
  | `cable_car`, `safari`, `theme`, `vinwonders`, `water_park` | 180 | 360 | 270 |
  | `night_market`, `market` | 90 | 150 | 120 |
  | `pagoda`, `temple`, `prison`, `museum` | 60 | 120 | 90 |
  | `beach`, `snorkel`, `island`, `boat` | 120 | 240 | 180 |

- **Best time.** Tokens are parsed from L220–L228 after stripping `Có`, `Exact type là`, `hoặc có` and splitting on `,` / `;`. Priority 10 and Default are skipped. The lowest priority wins. No match gives `all`. `canonical_candidate` comes from L236–L242, and it is the exact doc string, including the U+2013 dash (e.g. `Month 12–5`, `all_year`).
  - Existing rows that match: `beach` → beach_coast; `waterfall` → waterfall_green_season; `national_park`, `hiking_area` → forest_hiking; `museum`, `place_of_worship`, `church` → indoor_culture; `shopping_mall`, `market` → shopping_nightlife; `spa`, `massage` → spa_wellness; `amusement_park`, `water_park` → outdoor_entertainment.
  - Not matched, by design: `ferry_terminal`, `hindu_temple`, `buddhist_temple`, `wellness_center`, `boat_rental`. Exact match only (D-04).

## Ordering

1. Docs: fill §1.8 (Google table + Partner table) first. It is the oracle input for every value.
2. Seed blocks in `NB_SETUP_POI_ENTITY` / `NB_SETUP_POI_AMENITY`, then a byte-copy into `NB_SETUP_INITIAL_DDL`.
3. DDL, plan, MERGE and drift changes in the three notebooks; then the `NB_CREATE_DDL` patch cell.
4. Tests, then `python scripts/vv.py verify`.
5. Runtime: within each table, the order is backup → drop → apply → count. Place type goes before amenities, because amenity setup requires the entity edges, which already exist and are re-merged by the entity setup.

## Transaction and commit boundaries

- Each Delta statement is atomic: CTAS backup, `DROP TABLE`, `CREATE TABLE IF NOT EXISTS`, the seed `MERGE`, and the edge `MERGE`. Nothing spans two tables.
- Between `DROP` and the seed `MERGE` commit, the table is missing, then empty. The runbook covers that window by pausing `PL_VV_TRANS_SLV_TO_SLV_1H`.
- The repo change is one commit: docs, the four notebooks, three tests, and `01_DATA_MODEL.md`. Rollback reverts that one commit.

## Idempotency

- Re-running a setup notebook after success gives `inserted=0` and `drift=0`, because the MERGE is insert-only on the business key.
- The backup step uses `CREATE TABLE IF NOT EXISTS … AS SELECT`. A rerun never overwrites the first, pre-change snapshot. The runbook checks the backup count against the recorded pre-change count.
- The `NB_CREATE_DDL` patch adds only missing columns, and running it again changes nothing.
- The test oracle is deterministic and has no Spark dependency.

## Concurrency

- Only one operator runs the runbook. The 1H schedule is paused for the whole drop→verify window.
- If a 1H run starts anyway, `edge_status` returns `MISSING_TABLE` / `TABLE_RECREATED` and the node fails or recomputes. It fails loudly; it does not corrupt data.
- The setup notebooks already refuse to write edges while `PL_VV_TRANS_SLV_TO_SLV_1H` is running.
- Do not run `NB_SETUP_INITIAL_DDL` apply at the same time. Two concurrent insert-only MERGEs on an empty table could both commit. The dup-key checks after MERGE (`a1setupmerge`, `init_verify`) would raise.

## Retry and recovery

- The seed MERGEs keep `with_retry`.
- If apply fails after CREATE and before MERGE, the table exists with the new schema and no rows. Rerun apply: it inserts everything.
- If the edge MERGE fails, rerun it. It is idempotent.
- A code or seed defect found at runtime is handled by forward recovery: fix `SEED_ROWS` and the tests, re-deploy, then repeat runbook R4–R9 for the affected table. The backup already exists and is kept. Because the seed is insert-only, a value fix needs a drop and re-init.

## Partial failure

| Point of failure | State | Action |
|---|---|---|
| R2 backup | Nothing dropped | Fix and rerun R2 |
| R4/R5 (place type dropped, apply failed) | Table missing or empty; 1H paused | Rerun R5. If it fails for code reasons, roll back. |
| R5 done, R6/R7 failed | Place type rebuilt; amenities missing or empty | Rerun R6/R7. Keep 1H paused until R7 passes for both tables. |
| R8 (INITIAL_DDL plan) reports schema issues or `to_insert>0` | The mirror has drifted from the owner | Code defect: fix the mirror and rerun R8. Live data is already correct. |
| R10 1H shows unexpected downstream deltas | The dictionary is live | Investigate with the R10 queries. Roll back if the deltas cannot be explained. |

## Observability

- Plan JSON:
  - `NB_SETUP_POI_ENTITY`: `google`, `partner`, `missing_keys`, and the new `unseeded_rows`. `unseeded_rows` is `-1` for an old schema and `0` for an absent or clean table.
  - `NB_SETUP_POI_AMENITY`: `missing_keys`, `stale_keys`.
- Apply prints `inserted` and `drift`. `drift` now also compares `category_group` and the five columns in `NB_SETUP_INITIAL_DDL`, which previously did not compare `category_group`.
- The `NB_CREATE_DDL` patch prints the number of rows that still need a reseed.
- The runbook SQL (below) checks:
  - counts by source;
  - NULL counts;
  - counts by group and by best-time code;
  - the partner spot rows;
  - the downstream baseline against the result for `slv_poi_entity_non_enrich.category_group` and the active row count of `slv_poi_amenity`.
- The edge watermark reason after the rebuild should read `TABLE_RECREATED`.

## Security

- No secrets, no external calls, no PII. The reference data is public taxonomy.
- `DROP TABLE` runs only in the runbook, by the user, on Fabric DEV, against two fully qualified names. No notebook gains a `DROP` (naming rule 5; `test_no_destructive_sql`).
- The backup tables hold the same reference data and live in the same lakehouse.

## Rollout

The repository changes come first:
- Stop 0 (scope) and Stop 1 (D-07).
- Local tests and `vv.py verify`.
- Specialist review by `sql-data-reviewer`, `spark-runtime-reviewer` and `state-correctness-reviewer`, then `risk-gate`.

After that, the user syncs Fabric DEV to the commit and runs the runbook. The agent does not set `gates.runtime`. No production step is part of this task.

## Rollback and forward recovery

Forward recovery is preferred; see `Retry and recovery`.

Full rollback (runbook RB):
1. Pause 1H.
2. `git revert` the commit and sync DEV to it.
3. `DROP` both rebuilt tables.
4. Recreate each table with the old DDL text from the reverted `a1setupddl` / `c1setupddl`. This keeps the `NOT NULL` constraints, which a CTAS would lose and the old `EXPECTED` check would reject.
5. `INSERT INTO <table> (<old columns>) SELECT <old columns> FROM <table>_bak_20261020`.
6. Run the old setup notebooks with `p_apply=true`. Expect `inserted=0`, and expect drift equal to the pre-change drift.
7. Compare the counts with R2.
8. Resume 1H. The edges see `TABLE_RECREATED` and recompute.

The user decides when to drop the backups, after acceptance.

## Alternatives

| Option | For | Against | Decision |
|---|---|---|---|
| A1. Backup with CTAS → `DROP` → re-init through the owner setup notebook | User-approved. It exercises the same CREATE DDL a fresh environment uses, so DEV proves `a1setupddl`, `TABLE_SPECS` and the constraints. The row set equals the seed exactly. | Rollback needs a backup table plus the old DDL. The table id changes, which the lib handles as `TABLE_RECREATED`. | **Selected** |
| A2. `ALTER ADD COLUMNS` (patch cell) → `DELETE FROM` → re-seed; roll back with `RESTORE TABLE … VERSION AS OF` | Keeps the table id. Time-travel rollback without a copy. | Proves only the patch path, not CREATE. RESTORE depends on the VACUUM retention. Also a delete-and-rebuild, so no less risky. | Fallback if `DROP` is blocked in DEV |
| A3. `ALTER` + `MERGE WHEN MATCHED UPDATE` | No downtime window | Breaks the insert-only contract and the "giữ sửa tay" rule (`01_DATA_MODEL.md` L346, `test_setup_contract`) | Rejected |
| B1. 11-field literal rows | Required by request Constraints. Diffs are reviewable per row. | Long rows; authoring can introduce errors | **Selected**, guarded by `validate_seed` + the test oracle + pinned spot values |
| B2. Side dictionaries keyed by group or token, joined at load | Short | This is the code derivation the request bans | Rejected |
| B3. A `default_range` STRING column | Matches the doc text | Contradicts D-06 | Rejected |

Trade-off: A1 gives a little rollback convenience in exchange for proving the fresh-environment DDL and an exact seed state, and it is what the user approved. The oracle risk in B1 (authoring and tests sharing one bug) is reduced by literal spot assertions that do not depend on the oracle.

## Implementation plan

### Code: seed validation block (`a1setupseed`, mirrored in `init_seed_place_type`)

This replaces `CATEGORY_GROUPS`, `category_group`, `with_category_group` and the old `validate_seed`. `SEED_SECTORS`, `SEED_SKIP` and `SEED_ROWS` stay above it. `SEED_ROWS` rows become 11-tuples, for example:
`('google', 'beach', 'attraction', 'Beach', 'Biển', 'Light Sightseeing / Culture & Nature', 120, 240, 180, 'beach_coast', 'Month 12–4'),`

```python
CATEGORY_OTHER = "Other"
# Nhãn mục 1.8. Chỉ để kiểm tra; giá trị ghi sẵn trong từng dòng SEED_ROWS.
CATEGORY_GROUP_VALUES = (
    "Lodging", "Main Meals", "Light Snacks / Cafe", "Heavy Entertainment",
    "Light Sightseeing / Culture & Nature", "Shopping & Nightlife", CATEGORY_OTHER,
)
# Mục 1.9.2: candidate_best_time_code -> canonical_candidate. Chỉ để kiểm tra.
BEST_TIME_CANONICAL = {
    "snorkeling_diving": "Month 12–5", "island_boat": "Month 11–4", "beach_coast": "Month 12–4",
    "waterfall_green_season": "Month 6–10", "forest_hiking": "Month 11–3",
    "outdoor_entertainment": "Month 11–4", "indoor_culture": "all_year",
    "shopping_nightlife": "all_year", "spa_wellness": "all_year", "all": "all_year",
}
TOKEN_KEEP = ("suối", "thác")  # D-04: giữ đúng chữ


def validate_seed(rows):
    """Khóa trùng, source, sector, placeholder, token google, category_group, ước tính 1.9."""
    seen = set()
    token_re = re.compile(r"^[a-z0-9_]+$")
    allowed = set(SEED_SECTORS)
    skip = set(SEED_SKIP)
    for row in rows:
        if len(row) != 11:
            raise ValueError(f"{row[:2]}: {len(row)} trường, cần 11")
        source, place_type, sector, _cat, _cat_vi, group, low, high, avg, code, canonical = row
        key = (source, place_type)
        if key in seen:
            raise ValueError(f"duplicate key {key}")
        seen.add(key)
        if source not in {"google", "partner"}:
            raise ValueError(f"source {source!r}")
        if sector not in allowed:
            raise ValueError(f"sector {sector!r}")
        if place_type in skip:
            raise ValueError(f"place_type {place_type!r}")
        if source == "google" and place_type not in TOKEN_KEEP and token_re.fullmatch(place_type) is None:
            raise ValueError(f"bad token {place_type!r}")
        if group not in CATEGORY_GROUP_VALUES:
            raise ValueError(f"{key}: category_group {group!r}")
        if not all(type(v) is int for v in (low, high, avg)) or not low <= avg <= high:
            raise ValueError(f"{key}: range {low}-{high} avg {avg}")
        if BEST_TIME_CANONICAL.get(code) != canonical:
            raise ValueError(f"{key}: best time {code!r} -> {canonical!r}")
```

In `init_seed_place_type`, after `# END_PLACE_TYPE_SEED`:
```python
validate_seed(SEED_ROWS)
PLACE_TYPE_ROWS = list(SEED_ROWS)
```

### Code: `a1setupplan` changes

- `SEED_SCHEMA` appends `, range_low_min int, range_high_min int, avg_range_min int, candidate_best_time_code string, canonical_candidate string`.
- Delete `rows6 = with_category_group(SEED_ROWS)`, and use `seed_df = spark.createDataFrame(SEED_ROWS, SEED_SCHEMA)`.
- Add the unseeded-row guard below. Put `"unseeded_rows": int(unseeded)` in the PLAN JSON, and add the apply-time raise right after the `if not apply:` block.

```python
ESTIMATE_COLS = ("category_group", "range_low_min", "range_high_min", "avg_range_min",
                 "candidate_best_time_code", "canonical_candidate")
unseeded = 0
if table_exists(REF_FQ):
    have = {field.name.lower() for field in spark.table(REF_FQ).schema.fields}
    if set(ESTIMATE_COLS) <= have:
        cond = " OR ".join(f"{col} IS NULL" for col in ESTIMATE_COLS)
        unseeded = spark.sql(f"SELECT count(*) AS n FROM {REF_FQ} WHERE {cond}").first()["n"]
    else:
        unseeded = -1
print(f"unseeded_rows={unseeded}")
# ... existing `if not apply: notebookutils.notebook.exit(...)` (add "unseeded_rows") ...
if unseeded:
    raise ConfigError(f"{REF_FQ}: {unseeded} dòng thiếu cột/giá trị 1.8–1.9 (-1 = schema cũ). "
                      "Chạy runbook 20261020-dictionary-seed-from-mapping: xoá và init lại")
```

`missing_keys` is computed only on key columns, so it keeps working against the old schema.

### Code: `NB_CREATE_DDL` patch (new trailing cells)

The markdown cell `dictseedmd` contains `# [THÊM 20/10] 20261020-dictionary-seed-from-mapping`. The code cell `dictseedpy` contains:

```python
# [THÊM 20/10] 20261020-dictionary-seed-from-mapping
# ref_dictionary_place_type thêm 5 cột mục 1.9.1/1.9.2 (cho phép NULL). Không UPDATE giá trị:
# giá trị chỉ có trong SEED_ROWS của NB_SETUP_POI_ENTITY. Bảng đã có dòng thì chạy runbook xoá và init lại.
# ref_dictionary_amenities không đổi cột; 17 dòng mục 2.5 vào bằng NB_SETUP_POI_AMENITY.
PT_FQ = "lh_vv_silver.dbo.ref_dictionary_place_type"
NEW_COLS = (
    ("range_low_min", "INT"),
    ("range_high_min", "INT"),
    ("avg_range_min", "INT"),
    ("candidate_best_time_code", "STRING"),
    ("canonical_candidate", "STRING"),
)
if not spark.catalog.tableExists(PT_FQ):
    print(f"{PT_FQ} chưa có: chạy NB_SETUP_POI_ENTITY (CREATE đã có cột mới)")
else:
    have = {f.name.lower() for f in spark.table(PT_FQ).schema.fields}
    missing = [(c, t) for c, t in NEW_COLS if c not in have]
    if missing:
        spark.sql(f"ALTER TABLE {PT_FQ} ADD COLUMNS ({', '.join(f'{c} {t}' for c, t in missing)})")
    got = {f.name.lower(): f.dataType.simpleString() for f in spark.table(PT_FQ).schema.fields}
    bad = [(c, got.get(c)) for c, t in NEW_COLS if got.get(c) != t.lower()]
    if bad:
        raise RuntimeError(f"{PT_FQ}: cột patch sai {bad}")
    cond = " OR ".join(f"{c} IS NULL" for c, _t in NEW_COLS)
    n = spark.sql(f"SELECT count(*) AS n FROM {PT_FQ} WHERE {cond}").first()["n"]
    print(f"{PT_FQ}: {n} dòng chưa có giá trị 1.9 -> chạy runbook xoá và init lại" if n else f"{PT_FQ}: đủ cột và giá trị 1.9")
```

### DDL, MERGE and drift text (`a1setupddl`, `a1setupmerge`, `init_tables`, `init_plan`, `init_seed_write`)

- **CREATE** (after `category_group STRING`):
  ```
  ,
      range_low_min        INT,
      range_high_min       INT,
      avg_range_min        INT,
      candidate_best_time_code STRING,
      canonical_candidate  STRING
  ```
- **`EXPECTED`** appends `("range_low_min","int",True)`, `("range_high_min","int",True)`, `("avg_range_min","int",True)`, `("candidate_best_time_code","string",True)`, `("canonical_candidate","string",True)`.
- **ConfigError message.** Replace `chạy cell [THÊM 19/10] của NB_CREATE_DDL` with `chạy runbook 20261020-dictionary-seed-from-mapping (xoá và init lại)`.
- **`TABLE_SPECS`** appends `('range_low_min', 'INT', None)`, `('range_high_min', 'INT', None)`, `('avg_range_min', 'INT', None)`, `('candidate_best_time_code', 'STRING', None)`, `('canonical_candidate', 'STRING', None)`.
- **MERGE INSERT lists** (`a1setupmerge`, `_merge_place_type`) append the five columns, with values `s.range_low_min, s.range_high_min, s.avg_range_min, s.candidate_best_time_code, s.canonical_candidate`.
- **`init_plan`** view schema appends `, range_low_min INT, range_high_min INT, avg_range_min INT, candidate_best_time_code STRING, canonical_candidate STRING`.
- **Drift SQL.** `a1setupmerge` `DRIFT` and the `init_seed_write` place-type drift add `AND t.<c> <=> s.<c>` for each of the five columns. `init_seed_write` also adds `category_group`, which it was missing.

### Amenity seed (`c1setupseed`, mirrored in `init_seed_amenity`)

- `SEED_SECTORS = ("accommodation", "f_n_b", "attraction", "shopping_n_retail", "other")`.
- `SEED_GROUPS` gains `"other"`.
- Append one comment line, `# Mục 2.5 (D-05): flag chưa có -> other/other, amenity = amenity_vi = amenity_raw.`, followed by 17 rows of the form `(‘google’, ‘other’, ‘other’, t, t, t)`. The order is `takeout`, `curbsidePickup`, `reservable`, `servesBreakfast`, `servesLunch`, `servesDinner`, `servesBeer`, `servesWine`, `servesBrunch`, `servesVegetarianFood`, `menuForChildren`, `servesDessert`, `servesCoffee`, `allowsDogs`, `pureServiceAreaBusiness`, `acceptsDebitCards`, `acceptsNfc`.

### Docs

- **`mapping_place_type.md` §1.8.** Directly under the heading `# **1.8. Category Group**`, add:
  1. A table `| category_group | Google place_type |` with one row per `CATEGORY_GROUPS` group, listing its tokens in the current order, as backticked tokens separated by commas.
  2. The line: place_type không có trong bảng: `Other`.
  3. A table `| Partner Portal Enum | category_group |` with one row per partner enum in seed order, using the D-03 values.

  Neither header may contain `Google Place API` or `Partner Portal Enum (` in a way that `parse_mapping` treats as a column header. `parse_mapping` will skip §1.8+ anyway (below).
- Do not touch L186–L270.
- **`mapping_amenities.md`**: no edit. §2.5 already lists the tokens. Verify the file is byte-identical to the working tree.
- **`01_DATA_MODEL.md` L343–L344** (after Stop 0):
  - Columns: add the five new columns.
  - Seed for place type: 387 rows (328 google + 59 partner). `category_group` and the §1.9.1/§1.9.2 values are hard-coded per row from §1.8/§1.9. Changing the seed requires a drop and re-init per the runbook.
  - Seed for amenities: 175 rows (101 google + 74 partner), including 17 rows `other/other` from §2.5.
  - Replace the `[SỬA 19/10] … Backfill chỉ dòng đang NULL` sentence.

### Runtime runbook (Main copies it to `runtime-runbook.md`; the user runs it in Fabric DEV)

- **R0. Preconditions.** The commit is synced to DEV, local verification is green, and D-07 is recorded.
- **R1. Pause.** Disable the `PL_VV_TRANS_SLV_TO_SLV_1H` schedule and confirm no run is active (Fabric Monitor).
- **R2. Baseline and backup.**
  ```sql
  SELECT source_name, count(*) n FROM lh_vv_silver.dbo.ref_dictionary_place_type GROUP BY 1;  -- record (expect google 297, partner 59)
  SELECT source_name, count(*) n FROM lh_vv_silver.dbo.ref_dictionary_amenities GROUP BY 1;   -- record (expect google 84, partner 74)
  SELECT category_group, count(*) n FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich WHERE deleted_at IS NULL GROUP BY 1;
  SELECT count(*) n FROM lh_vv_silver.dbo.slv_poi_amenity WHERE deleted_at IS NULL;
  CREATE TABLE IF NOT EXISTS lh_vv_silver.dbo.ref_dictionary_place_type_bak_20261020 USING DELTA AS SELECT * FROM lh_vv_silver.dbo.ref_dictionary_place_type;
  CREATE TABLE IF NOT EXISTS lh_vv_silver.dbo.ref_dictionary_amenities_bak_20261020 USING DELTA AS SELECT * FROM lh_vv_silver.dbo.ref_dictionary_amenities;
  SELECT count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type_bak_20261020;  -- = R2 place total
  SELECT count(*) FROM lh_vv_silver.dbo.ref_dictionary_amenities_bak_20261020;   -- = R2 amenity total
  ```
- **R3. Plan (no writes).**
  - `NB_SETUP_POI_ENTITY` with `p_apply=false` → expect `PLAN`, `google=328`, `partner=59`, `missing_keys=31`, `unseeded_rows=-1`.
  - `NB_SETUP_POI_AMENITY` with `p_apply=false` → expect `google=101`, `partner=74`, `missing_keys=17`, `stale_keys=0`.
  - **STOP:** the user reviews before any drop.
- **R4.** `DROP TABLE lh_vv_silver.dbo.ref_dictionary_place_type;`
- **R5.** `NB_SETUP_POI_ENTITY` with `p_apply=true` → expect `inserted=387`, `drift=0`, status `SUCCESS`.
- **R6.** `DROP TABLE lh_vv_silver.dbo.ref_dictionary_amenities;`, then `NB_SETUP_POI_AMENITY` with `p_apply=true` → expect `inserted=175`, `drift=0`.
- **R7. Counts.**
  ```sql
  SELECT source_name, count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type GROUP BY 1;            -- google 328, partner 59
  SELECT count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type
   WHERE category_group IS NULL OR range_low_min IS NULL OR range_high_min IS NULL OR avg_range_min IS NULL
      OR candidate_best_time_code IS NULL OR canonical_candidate IS NULL;                              -- 0
  SELECT category_group, count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type GROUP BY 1 ORDER BY 1;
  SELECT candidate_best_time_code, canonical_candidate, count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type GROUP BY 1, 2 ORDER BY 1;
  SELECT place_type, category_group, range_low_min, range_high_min, avg_range_min FROM lh_vv_silver.dbo.ref_dictionary_place_type
   WHERE source_name = 'partner' AND place_type IN ('Hotel', 'Homestay', 'Café', 'Vietnamese', 'Car with Driver');
  SELECT source_name, business_sector, count(*) FROM lh_vv_silver.dbo.ref_dictionary_amenities GROUP BY 1, 2;  -- google/other = 17; totals 101 / 74
  ```
- **R8.** `NB_SETUP_INITIAL_DDL` with `p_apply=false` → no `ConfigError`; `seeds.place_type.to_insert=0`, `seeds.amenities.to_insert=0`.
- **R9.** Run the `NB_CREATE_DDL` cell `dictseedpy` → prints `đủ cột và giá trị 1.9`.
- **R10.** Resume 1H. After the first run:
  - The edge reason is `TABLE_RECREATED`.
  - Re-run the two R2 downstream queries. The `category_group` distribution and the `slv_poi_amenity` count should equal the baseline, because the node does not read partner-row groups and the 17 amenity rows are inert. List and explain any delta.
- **R11.** Record the outputs in the task evidence. The user sets `gates.runtime`.
- **R12.** Drop `*_bak_20261020` only after the user accepts.
- **RB.** Rollback: see `Rollback and forward recovery`.

## Verification

- **Local** (Windows PowerShell): `python -m pytest tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py -q`, then `python -m pytest -q`, then `python scripts/vv.py verify`.
- **Existing tests that must be changed:**
  - `test_poi_entity_contract.py`: `parse_mapping` (skip sections that are not in `SECTOR`), `test_seed_matches_mapping_file`, `test_seed_keys_unique_and_tokens_valid`, `test_seed_counts`, `test_setup_contract`, `test_create_ddl_patch`. Replace `test_category_groups_seed` and `test_partner_group_resolution_on_seed`.
  - `test_poi_amenity_contract.py`: `parse_mapping` (skip 2.5), `test_seed_matches_mapping_file`, `test_seed_counts`, `test_seed_sectors_groups`.
  - `test_initial_ddl_contract.py`: `test_ref_seed_blocks_identical`, line 406.

  Note: with today's working-tree docs, both `parse_mapping` functions already raise `KeyError` on `1.8` / `2.5`, because `SECTOR[...]` has no such entry. This change fixes that.
- **New tests:** listed in the brief. The oracle derives the expected values from the docs. The pinned literals are independent of the oracle.
- **Runtime:** runbook R3–R10 on Fabric DEV, run by the user.
