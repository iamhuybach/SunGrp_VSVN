# Model design: 20261109-srv-poi-amenity-en

## Scope

- Base task: `20261109-srv-poi-amenity-en`. This is model design round 2 (architecture round 1, M-2 re-run).
- `proposal.md` does not exist in the task folder. Rules are taken from the `decision.md` `## Quyết định hiện hành` ledger and the author input. `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited (see Conflict 1).
- Ledger rows implemented:
  - D-01: JSON tree `data[].amenity_group` (string), `data[].items[]` = `amenity_code`, `amenity_label_en`, `amenity_label_vi`, `service_flags`.
  - D-02: path `/api/v1/pois/{poi_id}/amenities` unchanged. Query `lang` stays removed (decision history 2026-11-09).
  - U-1: `amenity` code rule = architecture option B plus a diacritic fold.
  - U-2: JSON `items[].service_flags` reads column `service_flags`.
  - U-3: the user drops `lh_vv_silver.dbo.ref_dictionary_amenities` and reruns `NB_SETUP_POI_AMENITY p_apply=true`. The runbook text is out of scope.
- Change in one line: the current English display string moves to a new column `amenity_en` on every amenity table. `amenity` becomes the U-1 snake_case code, computed from that string.
- Out of scope: API classes, MERGE, locks, ordering, rollout, runbook text.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.ref_dictionary_amenities` | silver (reference) | one row per (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`) | `NB_SETUP_POI_AMENITY` (`c1setupseed`, `c1setupddl`, `c1setupmerge`). DDL mirror: `NB_SETUP_INITIAL_DDL` (ref column list, `init_seed_amenity`) |
| `lh_vv_silver.dbo.slv_poi_amenity` | silver | one row per (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). Unchanged. | `NB_SLV_POI_AMENITY` (`d1amenbuild`). DDL: `NB_SETUP_POI_AMENITY` `c1setupddl`, `NB_SETUP_INITIAL_DDL` |
| `lh_vv_gold.dbo.gld_srv_poi_amenity` | gold (serving) | one row per (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). Unchanged. | `NB_GLD_SRV_POI_AMENITY` (`srvamenitybuild`). DDL: `NB_CREATE_DDL` `AMENITY_COLS`, `NB_SETUP_INITIAL_DDL` |
| `apps.srv_poi_amenity` (PostgreSQL) | serving | one row per (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). Unchanged. | DDL: `sql/postgres/gld_srv_serve.pg.sql`. Sync notebook: not in the read set (Conflict 7) |

## Keys

- `ref_dictionary_amenities`
  - Business/natural key (MERGE key in `c1setupmerge` and `init_seed_amenity`): (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`). Unchanged. `amenity` now holds the U-1 code. `amenity_en` is not added to the key (author input "Still true").
  - Uniqueness after the change: the only 4-column duplicate allowed by `AMENITY_SHARED_RAW` is the google/attraction/facilities_and_services `goodForChildren` pair. Under U-1 it produces two different codes, `good_for_children` and `family_friendly`, so the 5-column key stays unique (architecture `Verdict and blocking items`, U-1 note).
  - Foreign keys: none declared.
- `slv_poi_amenity`
  - Primary/MERGE key: (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). Unchanged (`SPEC.pk`).
  - `poi_id` formula source: `build` takes `poi_id` from the input tables `slv_3p_poi_amenity` and `slv_poi_entity_non_enrich`. It does not hash or derive it. `docs/context/mapping_gld_srv_poi_amenity.md` §0 records the hash formula in this notebook as `MISSING`. This design does not change `poi_id`.
  - Logical references (not enforced): `poi_id` → `slv_poi_entity_non_enrich.poi_id`. (`business_sector`, `amenity_group`, `amenity_raw`, `amenity`) → the matched google row of `ref_dictionary_amenities`.
- `gld_srv_poi_amenity`
  - Primary/MERGE key: (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). Unchanged (`SPEC.pk` in `srvamenitybuild`). `poi_id` passes through from `slv_poi_amenity`.
  - Foreign keys: none.
- `apps.srv_poi_amenity`
  - `PRIMARY KEY (poi_id, business_sector, amenity_group, amenity_raw)`. Unchanged. `poi_id` comes from gold.
  - Foreign keys: none declared in `gld_srv_serve.pg.sql`.

## Columns

U-1 code rule, referenced below as **RULE-U1**. It applies to each seed `amenity_en` value.

1. Split camelCase: put a boundary between a lowercase letter and the uppercase letter that follows it (option B).
2. Lowercase.
3. Replace each run of Unicode non-word characters or `_` with one `_` (option A).
4. Strip `_` at both ends (option A).
5. Fold accented letters to the base letter (U-1 user addition). The seed `amenity_en` values contain one non-ASCII letter, `é`, which becomes `e`. No Vietnamese-specific rule is added.

Worked results: `servesWine` → `serves_wine`; `Pet Café` → `pet_cafe`. The other architecture U-1 table rows keep their option B outputs. The only change is `pet_café` → `pet_cafe`.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `ref_dictionary_amenities` | `amenity_en` | `STRING` | NOT NULL | Seed tuple field that today holds the English display string (the 5th field of `SEED_ROWS` / `AMENITY_ROWS`) | New column. It keeps the current `amenity` string unchanged (author input "Still true"). It is NOT NULL like `amenity` because U-3 drops and reseeds the table, so no existing rows need a backfill. |
| `ref_dictionary_amenities` | `amenity` | `STRING` | NOT NULL (unchanged) | RULE-U1 applied to `amenity_en` of the same seed row | U-1. Stays in the 5-column key. The seed must carry the computed code. Under U-3 the old key values are discarded by DROP and reseed. |
| `ref_dictionary_amenities` | `service_flags` | `STRING` | nullable (unchanged) | Seed | Unchanged. U-2 confirms that this column feeds the JSON `service_flags`. |
| `slv_poi_amenity` | `amenity_en` | `STRING` | nullable | `ref_dictionary_amenities.amenity_en` of the matched condition row | New column. It is added to `OUT_COLS`. It comes from the same matched dictionary row as `service_flags` (the D10 comment in `d1amenbuild`). Gold needs it on slv (author input "Still true"). Nullable like the slv `amenity` column (Conflict 5). |
| `slv_poi_amenity` | `amenity` | `STRING` | nullable (unchanged) | `ref_dictionary_amenities.amenity` of the matched row | Value is now the U-1 code. No code change in slv. |
| `slv_poi_amenity` | `service_flags` | `STRING` | nullable (unchanged) | matched ref row | Unchanged (U-2). |
| `gld_srv_poi_amenity` | `amenity_en` | `STRING` | nullable | `slv_poi_amenity.amenity_en` | New column. It is added to `OUT_COLS` and to `NB_CREATE_DDL` `AMENITY_COLS`. `build` stays `select(*OUT_COLS)` (author input "Still true"). |
| `gld_srv_poi_amenity` | `amenity` | `STRING` | nullable (unchanged) | `slv_poi_amenity.amenity` | 1-1 pass-through. The value is now the U-1 code. |
| `apps.srv_poi_amenity` | `amenity_en` | `text` | nullable | `gld_srv_poi_amenity.amenity_en` | New column. It matches gold (author input "Still true"). |
| `apps.srv_poi_amenity` | `amenity` | `text` | nullable (unchanged) | gold | Value is now the U-1 code. |
| `apps.srv_poi_amenity` | `service_flags` | `text` | nullable (unchanged) | gold | U-2: this column is the JSON `service_flags` source, not `amenity_vi`. |

JSON field sources for `/api/v1/pois/{poi_id}/amenities` (D-01, D-02, U-2). This is a source map only. No API class design.

| JSON field | `apps.srv_poi_amenity` column |
|---|---|
| `data[].amenity_group` | `amenity_group` |
| `data[].items[].amenity_code` | `amenity` |
| `data[].items[].amenity_label_en` | `amenity_en` |
| `data[].items[].amenity_label_vi` | `amenity_vi` |
| `data[].items[].service_flags` | `service_flags` (U-2) |

## Lineage

- `ref_dictionary_amenities`
  - Bronze: none.
  - Silver: none. It is seeded from literals in `NB_SETUP_POI_AMENITY` `c1setupseed` and mirrored in `NB_SETUP_INITIAL_DDL` `init_seed_amenity`. Both seed literals carry `amenity_en` and the RULE-U1 `amenity`.
  - Gold: none.
- `slv_poi_amenity`
  - Bronze: none read directly. Upstream, `slv_3p_poi_amenity` is loaded from `brz_3rd_crawler_poi_stream`, which this task does not change.
  - Silver reads: `slv_3p_poi_amenity` (`poi_id`, `source_flags_json`), `slv_poi_entity_non_enrich` (`poi_id`, `business_sector`, `source_name`, `types_json`), and `ref_dictionary_amenities`. The google rows with `is_active = true` now also supply `amenity_en`.
  - Gold reads: none.
- `gld_srv_poi_amenity`
  - Bronze: none.
  - Silver reads: `slv_poi_amenity` only.
  - Gold reads: none, so gold never reads gold. It does not read `ref_dictionary_amenities`.
- `apps.srv_poi_amenity`
  - Reads `lh_vv_gold.dbo.gld_srv_poi_amenity` only. It does not read silver or the ref table.

## Conflicts and questions

1. **Proposal missing.** The handoff says to cite `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`, but `proposal.md`, `problem-analysis.md`, and `requirements-analysis.md` are absent. This design cites the ledger and the author input instead.
   - No `ctrl_cfg_schema_registry` change is shown in the read set, so none is designed.
   - No pipeline edge changes are designed: the three slv edges and the one gold edge stay as they are.
2. **Closed: snake_case rule (prior model-design Conflict 2).** U-1 closes it: option B plus a fold of `é` to `e`. Results are recorded under RULE-U1.
   - Every non-ASCII letter in the seed `amenity_en` values has an output. The only one is `é`, in `Pet Café`.
   - Non-ASCII characters in `amenity_raw` and `amenity_vi` (Vietnamese letters, the en dash) are never inputs to RULE-U1, so they need no output.
   - The seed needs only a lowercase-to-uppercase boundary for the camelCase split. No seed value contains a digit-to-uppercase or acronym-to-word boundary such as `XMLParser`. If Main's split also inserts boundaries there, those cases have no seed evidence.
3. **Closed: JSON `service_flags` source (prior Conflict 3).** U-2 closes it. The source is `apps.srv_poi_amenity.service_flags`. `amenity_label_vi` still reads `amenity_vi`. This replaces the earlier request/history mapping that used `amenity_vi`.
4. **Recorded as resolved by architecture (prior Conflicts 4, 7, 8, 10).** Per architecture M-2, these were resolved in `architecture.md` `## Grain and keys`. This design does not reopen them. The slv/gold/PostgreSQL grain stays (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). That section was outside this pass's read set.
5. **Closed: ref drop/reseed and `amenity_en` nullability (prior Conflicts 5 and 6).**
   - U-3 closes it: the user drops `ref_dictionary_amenities` and reruns `NB_SETUP_POI_AMENITY p_apply=true`. That is why ref `amenity_en` is `NOT NULL` like `amenity`, and the 5-column key with the new `amenity` code needs no in-place migration.
   - Slv, gold, and PostgreSQL `amenity_en` are modeled as nullable, following the existing nullability of `amenity` in each of those tables. No ledger row requires `NOT NULL` there. Confirm if a stricter rule is wanted.
6. **Column position (question).** `c1setupddl` `EXPECTED` and `NB_CREATE_DDL` `_want`/`_schema` compare ordered column lists. Recommendation: put `amenity_en` right after `amenity` in every table and in `SEED_SCHEMA`, `COND_SCHEMA`, `OUT_COLS`, `AMENITY_COLS`, the `NB_SETUP_INITIAL_DDL` lists, and the PostgreSQL DDL. Confirm, or take the order from `architecture.md` `## Implementation plan`, which was not read in this pass.
7. **Unknowns outside the read set.**
   - (a) `match_conditions` in `NB_SLV_POI_AMENITY` builds the tuples that `COND_SCHEMA` describes, and the metrics read positions `c[5]` and `c[-3]`. It must carry `amenity_en` in the same position as `COND_SCHEMA`. Its body was not read.
   - (b) The notebook or job that loads `apps.srv_poi_amenity` from gold was not in the read set. Its column list must add `amenity_en`.
   - (c) The `docs/context/01_DATA_MODEL.md` rows `ref_dictionary_amenities` and N7 `slv_poi_amenity`, and `docs/context/mapping_gld_srv_poi_amenity.md` §0 and §1, list the columns without `amenity_en`. They need the column and the RULE-U1 description (architecture M-1).
