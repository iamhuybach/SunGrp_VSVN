# Model design: 20261125-legacy-init-destination-and-poi-name

## Scope

- Base task: `20261119-legacy-gold-poi-init`. Its `Quyết định hiện hành` D-01 (only the init notebook reads another gold), D-04 (`load_origin` STRING, init writes `LEGACY_INIT`, the pipeline sets it to NULL on its first MATCHED), D-05 (`gld_poi_legacy_id_map`, `NB_SETUP_LEGACY_GOLD_POI`) and D-06 (`poi_name` and `district` on `gld_srv_poi_info` come from the `lang = vi` row) still apply.
- This task's ledger rows implemented here:
  - D-01: per-lang `poi_name` on `gld_srv_poi_multi_lang`.
  - D-02: the main flow writes `poi_name = null`.
  - D-03: the init notebook takes its target workspace as a parameter.
  - D-04: `destination_id` stays STRING.
- `proposal.md` does not exist in this task. Because of that, `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited. This design uses the ledger above, the author input, and the probe result `evidence/results/destination_id_non_legacy_shape.txt` instead. No `ctrl_cfg_schema_registry` row or `json_path` is added or changed. None of the files read show one for these columns.
- Out of scope:
  - MERGE shape, locks, ordering, idempotency mechanics and rollout.
  - `poi_name` in API JSON.
  - `destination_name`. Its current rule is unchanged.
  - `poi_name` on `gld_srv_poi_info`. It stays under base-task D-06.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `<target_ws>.lh_vv_gold.dbo.gld_srv_poi_info` | gold (serving) | one row per `poi_id` | Pipeline rows: `NB_GLD_SRV_POI_INFO` (unchanged). `LEGACY_INIT` rows: `NB_SETUP_LEGACY_GOLD_POI`, stage `info` |
| `<target_ws>.lh_vv_gold.dbo.gld_srv_poi_multi_lang` | gold (serving) | one row per `(poi_id, lang)` (unchanged, D-01) | Pipeline rows: `NB_GLD_SRV_POI_MULTI_LANG` (P1 and P2). `LEGACY_INIT` rows: `NB_SETUP_LEGACY_GOLD_POI`, stage `multi_lang`. DDL: `NB_SETUP_INITIAL_DDL` `init_tables` `TABLE_SPECS`, plus an additive `NB_CREATE_DDL` cell for existing tables |
| `apps.srv_poi_multi_lang` | PostgreSQL serving | one row per `(poi_id, lang)`, PK `(poi_id, lang)` | DDL `sql/postgres/gld_srv_serve.pg.sql`. The loader notebook is not among the files read |

`<target_ws>` is the workspace parameter from D-03. Today `id:lgpconst` hard-codes it as `sgr_visitvn_dev`.

`gld_poi_legacy_id_map` is read only. Its grain is one row per `legacy_poi_id`, and its model does not change.

## Keys

| table | primary key | business key | foreign keys / lookups |
|---|---|---|---|
| `gld_srv_poi_info` | `poi_id` | `poi_id` | `gld_poi_legacy_id_map.poi_id`, where `poi_id_status = 'OK'` |
| `gld_srv_poi_multi_lang` | `(poi_id, lang)`, same as NodeSpec `pk` in `id:srvmlbuild` | `(poi_id, lang)` | `poi_id` must have a live parent in `gld_srv_poi_info` for init rows (existing `parents` semi-join in `id:lgpmain`). `lang` comes from the map row's `lang`, which is `poi_master.lang` of the legacy row |
| `apps.srv_poi_multi_lang` | `(poi_id, lang)` | same | none |

How `poi_id` is computed (unchanged; reruns must not change `poi_id`):

- **Init:** `new_poi_id` in `id:lgppure` gives:
  - google: `uuid_md5('google', source_id)`. This matches `AGENTS.md` §7 third-party `HASH_MD5_UUID` = `uuid_format(md5(concat(source_name, source_id)))`.
  - partner: `uuid_md5(source_id, 'partner')`. This matches `AGENTS.md` §7 partner `uuid_format(md5(concat(id, 'partner')))`.
  - `source_name` comes from `legacy_source_name`, which maps `partner_portal` to `partner`.
  - A null or blank `source_id` gives a null `poi_id` with `poi_id_status = 'MISSING_EVIDENCE'`.
- **Main flow `NB_GLD_SRV_POI_MULTI_LANG`:**
  - P1 takes `poi_id` from `slv_enr_poi_info_multi_lang.poi_id`.
  - P2 uses `uuid_md5(business_service_id, 'partner')`, which matches `AGENTS.md` §7 partner.

`load_origin` is a technical column, not a key. It stays out of `TABLE_SPECS` and PostgreSQL, as in the base task.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_srv_poi_info` | `destination_id` | STRING (unchanged in `NB_CREATE_DDL` gold spec and `apps.srv_poi_info.destination_id text`) | yes | `LEGACY_INIT` rows: old gold `poi_master.destination_ids`. Pipeline rows: `slv_enr_poi_destination.destination_id`, 1-1 (`mapping_gld_srv_poi_info.md` §1.2, not changed) | Ledger D-04: keep STRING, no ARRAY. Author input: init no longer uses `get_json_object(destination_ids, '$[0]')`. It writes the whole old id array as one JSON array string of strings, the same shape as non-`LEGACY_INIT` rows (probe: 19797 `json_array_string`, 2 `json_array_empty`, 110 null, `bad=0`). If `destination_ids` is not a JSON array, or any element is not a string, init does not wrap it and does not take the first element; it stops with `user_decision` and reports the shape seen. If the old rows mapped to one new `poi_id` disagree on `destination_ids` across langs, init does not pick one; it stops with `user_decision`. Init updates only rows with `load_origin = 'LEGACY_INIT'`, including the existing Dev rows, and never updates pipeline-owned rows (author input; base D-04 and D-07). See questions 1–4 |
| `gld_srv_poi_multi_lang` | `poi_name` | STRING | yes | `LEGACY_INIT` rows: old gold `poi_master.poi_name` of the legacy row behind that `(poi_id, lang)`. `NB_GLD_SRV_POI_MULTI_LANG` P1 and P2: none, typed null | Ledger D-01: STRING, nullable. Grain stays `(poi_id, lang)`. Init takes the name of the same lang from the source the notebook already uses for names (`pm["poi_name"]` in `id:lgpmain`). It never applies the `vi` name to every row. Ledger D-02: the main flow writes `poi_name = null` on P1 and P2, and does not read a column `slv_enr_poi_info_multi_lang` lacks. P2 casts `poi_name` to the P1 type like the other P2 columns (`id:srvmlbuild` `_i18n_only`). The pipeline MERGE may overwrite an init `poi_name` with null once the row becomes a pipeline row. See questions 5–7 |
| `apps.srv_poi_multi_lang` | `poi_name` | text | yes | Loaded from `gld_srv_poi_multi_lang.poi_name` | `test_gold_and_pg_columns_and_types_match` requires the gold `TABLE_SPECS` columns from `init_tables` to equal the PostgreSQL columns minus `ingestion_ts`. Adding `poi_name STRING` to `TABLE_SPECS` therefore requires `poi_name text` on `apps.srv_poi_multi_lang` (author constraint: add only when `TABLE_SPECS` must match). Not added to API JSON. See question 8 |

## Lineage

**`gld_srv_poi_info.destination_id`**

- Bronze: none read directly.
- Silver:
  - Pipeline rows: `slv_enr_poi_destination`, via `NB_GLD_SRV_POI_INFO`, unchanged.
  - The init notebook reads `<target_ws>.lh_vv_silver.dbo.ref_dictionary_amenities`, but only for amenity, not for this column.
- Gold:
  - Init reads old gold `sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master` at the pinned version. This is the workspace already in `id:lgpconst` (`OLD`), and D-03 keeps it.
  - It also reads `<target_ws>.lh_vv_gold.dbo.gld_poi_legacy_id_map` and the target `gld_srv_poi_info` for existing keys.
  - These are gold-to-gold reads by the one-time init notebook only. Base-task D-01 allows that exception. The periodic pipeline does not read gold.

**`gld_srv_poi_multi_lang.poi_name`**

- Bronze: none.
- Silver: none for `poi_name`. The main flow keeps reading `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich` and `slv_pn_business_service_i18ns` for other columns, and `poi_name` is a literal null.
- Gold:
  - Init reads old gold `poi_master` (for `poi_name` and `lang`) and `poi_enrichment_display` (for the rows that already drive multi-lang init) in the old workspace, both at the pinned version.
  - It also reads `<target_ws>` `gld_poi_legacy_id_map` and `gld_srv_poi_info` (the `parents` set).
  - Same base-task D-01 exception. The main flow does not read gold.

**`apps.srv_poi_multi_lang.poi_name`**

- Reads `lh_vv_gold.dbo.gld_srv_poi_multi_lang` only (`AGENTS.md` §7 serving rule). No bronze or silver.

## Conflicts and questions

1. **Which rows are compared across langs for `destination_id`.** `id:lgpmain` currently builds `master_rows` only from `poi_master` rows with `lang = 'vi'`, chosen through `vi_key`. The author input says that if several langs of the same old `poi_id` have different `destination_ids`, init must stop. At the pin, old `poi_master.poi_id` is unique per row and the map has one `lang` per `legacy_poi_id`. So "the same old `poi_id` across langs" can only mean all legacy rows that map to one new `poi_id`. Should the check compare every lang row mapped to the new `poi_id`, not only `vi`? And if there is no `vi` row, should `destination_id` come from the other lang rows, or stay null as it does now?
2. **Serialization of the JSON array string.** The probe classified non-`LEGACY_INIT` values only by shape. It did not show their exact text form: separators or spacing, element order, or duplicate handling. Should init keep the old array's element order and text, re-serialize it in a fixed form, or match whatever form the pipeline writes? Comparing old and new values (for question 1, and for re-run stability) depends on this.
3. **Empty array and null.** Non-`LEGACY_INIT` rows include 2 empty arrays and 110 nulls. For an old `destination_ids` that is `[]`, should init write the empty JSON array string or null? For a null `destination_ids`, is null correct? The author input gives no rule for either.
4. **Shape of the `user_decision` stop.** "Stop `user_decision` with the shape seen" needs a fixed set of shape classes to report. The probe uses `json_array_string`, `json_array_null_elem`, `json_array_empty`, `null` and `bad`. Should init report these same classes, with `bad` split into not-JSON, not-array and non-string element? Does an array that contains a null element count as "element not a string" and stop?
5. **Conflicts on `poi_name` within one `(poi_id, lang)`.** Multi-lang init groups `(poi_id, lang)` with `single_payload` and drops keys that have more than one payload. If two legacy rows map to the same `(poi_id, lang)` with the same display payload but different `poi_master.poi_name`, should `poi_name` join the payload, so the key counts as a conflict and is not written? Or should this case be a `user_decision` stop? Picking one name is excluded by D-01.
6. **Which legacy row supplies the name.** Should the join key be `poi_master.poi_id = poi_enrichment_display.poi_id`, the legacy row that already drives the multi-lang row through `mp.legacy_poi_id`? Or should it be `poi_master` matched on the map's `(poi_id, lang)`? Both give the same lang, because `mp.lang` comes from `poi_master.lang`. They differ only when question 5 applies. Note that `lang_mismatch_n` counts display rows whose `lang` differs from the map's `lang`. The target `lang` and `poi_name` follow the map's `lang`, as `picked` does today.
7. **Column position.** None of the files read fixes where `poi_name` goes in `gld_srv_poi_multi_lang` and `apps.srv_poi_multi_lang`. Earlier additions (`experience`) went in before `row_hash`, and a PostgreSQL `ADD COLUMN` lands at the end of the table. Confirm the position for `TABLE_SPECS`, the `NB_CREATE_DDL` additive cell, `OUT_COLS`, and the PostgreSQL `CREATE TABLE`.
8. **Conflict with "no API JSON".** `test_entities_match_gold_columns_types_and_keys` requires the JPA entity `SrvPoiMultiLang` columns to equal the gold `TABLE_SPECS` columns once `services/data-serving-service` exists. Adding `poi_name` to gold therefore forces an entity field. Can the field be added to the entity but kept out of the API response DTO? Or should the test or contract be handled another way? The entity and DTO files were not in the read set.
9. **Workspace for the dictionary table.** D-03 parameterizes the target workspace. `DICT_FQ` (`lh_vv_silver.dbo.ref_dictionary_amenities`) is hard-coded to `sgr_visitvn_dev` too. Should it use the same target-workspace parameter? The `OLD` workspace stays as it is in the notebook, per D-03. The guards `_workspace_name() != "sgr_visitvn_dev"` and `fq.startswith("sgr_visitvn_dev.")` also name the workspace. Changing them is not a model decision, but the Architect needs to know they exist.
10. **`destination_name` is not covered.** Init writes `destination_name` from `poi_master.destination_names` of the `vi` row without parsing it. The request does not ask to align it with the new array form of `destination_id`. Confirm it stays unchanged.
