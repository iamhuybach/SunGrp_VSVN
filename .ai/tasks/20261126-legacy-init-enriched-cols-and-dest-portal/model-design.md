# Model design: 20261126-legacy-init-enriched-cols-and-dest-portal

## Scope

Base task: `20261126-legacy-init-enriched-cols-and-dest-portal`. In `task-state.yaml` the status is `waiting_architecture`, gate `evidence` is `pass`, and the signals are `data_model_change`, `data_evidence_required`, and `runtime_proof_required`. This document replaces the earlier `model-design.md`. Ledger rows `D-INIT-KEY`, `D-INIT-INFO-VI`, `D-INIT-ENRICH-ONLY`, `D-DEST-BACKFILL`, and `D-LEGACY-DEST` close its Conflicts 1, 2, 5, and 6.

The task has no `proposal.md`, `problem-analysis.md`, or `requirements-analysis.md`, so this document cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. The requirement comes from the `decision.md` `## Quyết định hiện hành` ledger. Where the ledger and `request.md` differ, the ledger wins. Probe facts come from `evidence/results/p_gaps.txt` and `evidence/results/ai_enriched_poi_schema.txt`.

This design covers two changes in one task (`D-ONE-TASK`):

1. **Legacy init of six gold-only columns** from `sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_enriched_poi`, written by `NB_SETUP_LEGACY_GOLD_POI` `lgpmain`.
   - Ledger rows: `D-SCHEMA`, `D-MAP-OLD-ADDR`, `D-MAP-PRICE-LEVEL`, `D-MAP-PRICE-MIN`, `D-MAP-PRICE-MAX`, `D-MAP-STORY`, `D-MAP-TIPS`, `D-LANG-ROW`, `D-PRICE-TYPE`, `D-GOLD-ONLY`, `D-LEGACY-READ`, `D-OLD-ADDR`, `D-NO-GOLD-COL`, `D-INIT-KEY`, `D-INIT-INFO-VI`, `D-INIT-ENRICH-ONLY`.
2. **Destination projection** on `slv_enr_poi_destination`: a new `destination_portal_id`, a new source for `destination_id`, an in-place backfill of existing silver rows, and the knock-on effect on `gld_srv_poi_info.destination_id`.
   - Ledger rows: `D-DEST-ID`, `D-DEST-PORTAL`, `D-DEST-NAME`, `D-DEST-ARRAY`, `D-DEST-SCOPE`, `D-DEST-GOLD`, `D-DEST-BACKFILL`, `D-LEGACY-DEST`.

`D-G4` adds three files to scope: `tests/test_enr_extract_contract.py`, `tests/test_legacy_gold_poi_init_contract.py`, and `docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md`. They hold no model content of their own. The model rules below are what those tests and that doc must reflect.

Out of scope, because they belong to the Architect (`architecture.md` §3–§16):
- invariants, state ownership, locking, transaction and commit boundaries, ordering, idempotency, retry, recovery, and rollout;
- PostgreSQL, Java/API, and `docs/context/api-mapping/` (`D-GOLD-ONLY`, `D-DEST-SCOPE`).

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_enr_poi_destination` | silver | One row per `poi_id`. Registry `"key": "poi_id"` (`NB_SETUP_INITIAL_DDL` `init_cfg_enr`; `NB_CREATE_DDL` `enrbrzcfgpy`). Load mode `DOC` (`NB_SETUP_INITIAL_DDL` edge `brz_enrichment_result` → `slv_enr_poi_destination`). Grain unchanged. | `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` (`enr04` projection). One-time in-place backfill of existing rows: `NB_CREATE_DDL`, cell named in `architecture.md` §8.5–§8.6. |
| `lh_vv_gold.dbo.gld_srv_poi_info` | gold | One row per `poi_id`, no lang. Unchanged (`D-NO-GOLD-COL`). | `NB_GLD_SRV_POI_INFO` (pipeline, `PL_VV_TRANS_SLV_TO_GLD_30M`, `RECOMPUTE`). `NB_SETUP_LEGACY_GOLD_POI` `lgpmain`, stage `info` (one-time init). |
| `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | gold | One row per `(poi_id, lang)`. Unchanged (`D-NO-GOLD-COL`). | `NB_GLD_SRV_POI_MULTI_LANG` (pipeline). `NB_SETUP_LEGACY_GOLD_POI` `lgpmain`, stage `multi_lang` (one-time init). |
| `sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_enriched_poi` | legacy gold, read-only init source | One row per legacy `poi_id`, and each row carries one `lang`. Counts: 136754 rows, 136754 distinct `poi_id`, 0 null `poi_id`, 0 null or blank `lang`, 0 duplicate `(poi_id, lang)` (`ai_enriched_poi_schema.txt`). By lang: `en` 45659, `vi` 45674, `ko` 45421 (`p_gaps.txt` P-AI-2). | Not applicable (not written). |

## Keys

**`slv_enr_poi_destination`**
- Primary / MERGE key: `poi_id`, from registry `"key": "poi_id"`. Unchanged.
- Business key: `poi_id`, read from bronze `_doc.poi_id` (registry `"poi_id": _enr("_doc.poi_id")`). The bronze producer computes it. The formula follows `AGENTS.md` §7:
  - third party: `uuid_format(md5(concat(source_name, source_id)))`;
  - partner: `uuid_md5(id, 'partner')`.
- Backfill match key: each existing silver row is matched to the bronze `brz_enrichment_result` event that produced it (`D-DEST-BACKFILL`). The match tuple is set in `architecture.md` §8.6. P-DEST-1 found an event for every silver row: `joined_rows` = `silver_n` = 19799 and `no_event_n` = 0.
- Foreign keys: none declared. `poi_id` reaches `gld_srv_poi_info.poi_id` through the `NB_GLD_SRV_POI_INFO` edge.

**`gld_srv_poi_info`**
- Primary / MERGE key: `poi_id`. It is `STRING NOT NULL` in `TABLE_SPECS`, and `lgpmain` writes with pk `("poi_id",)`. Unchanged.
- Business key on init rows: `gld_poi_legacy_id_map.poi_id`, computed by `lgppure.new_poi_id` (formula in `mapping_legacy_gold_to_gld_srv.md` lines 7–12):
  - `google`: `uuid_md5('google', source_id)`;
  - `partner_portal` → `partner`: `uuid_md5(source_id, 'partner')`.
- Foreign key for `old_address`, `price_level`, `price_min`, `price_max` (`D-INIT-KEY`, `D-INIT-INFO-VI`): `ai_enriched_poi.poi_id` = `vi_key.poi_id`, the legacy `poi_id` of the `lang = vi` row that `vi_key` picks, with `ai_enriched_poi.lang = 'vi'`. Then `vi_key._new` becomes `poi_id`.
  - P-AI-1 matched every row to `gld_poi_legacy_id_map.legacy_poi_id`: `map_hit_n` = `map_same_lang_n` = `map_ok_n` = 136754 and `new_id_hit_n` = 0. So `ai_enriched_poi.poi_id` is the legacy id, not the new id.

**`gld_srv_poi_multi_lang`**
- Primary / MERGE key: `(poi_id, lang)`. Both are `STRING NOT NULL` in `TABLE_SPECS`, and the init pk is `("poi_id", "lang")`. Unchanged.
- Business key on init rows: `gld_poi_legacy_id_map.poi_id`, same formula source as above. `lang` is `gld_poi_legacy_id_map.lang`, which is `poi_master.lang`.
- Foreign key for `story` and `local_tips` (`D-INIT-KEY`, `D-LANG-ROW`): `ai_enriched_poi.poi_id` = `gld_poi_legacy_id_map.legacy_poi_id` and `ai_enriched_poi.lang` = `gld_poi_legacy_id_map.lang`. Then `(map.poi_id, map.lang)` is the target key. Under `D-INIT-KEY`, a lang mismatch stops RUN.

**`ai_enriched_poi`**
- Observed unique key: `poi_id`. `(poi_id, lang)` is also unique (`ai_enriched_poi_schema.txt`).

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_enr_poi_destination` | `destination_id` | STRING | yes (unchanged in `TABLE_SPECS`) | bronze `brz_enrichment_result`, block `destinations`, each element's `strapi_document_id` (registry `_enr("destinations.strapi_document_id")`, `architecture.md` §8.3) | `D-DEST-ID`, `D-DEST-ARRAY`. A JSON array string, one entry per element in source order, null kept where an element is null. The element field is a string: P-DEST-2 `sd_string_n` = `elem_n` = 43241, `sd_number_n` = 0. Backfill of existing rows: `D-DEST-BACKFILL`. The 2 rows with no `strapi_document_id` elements (P-DEST-1 `sd_none_n` = 2) store an empty JSON array. |
| `slv_enr_poi_destination` | `destination_portal_id` (new) | STRING | yes (`02_NAMING_CONVENTION.md` rule 5: a column added to an existing table must allow NULL) | bronze `brz_enrichment_result`, block `destinations`, each element's `id` (registry `_enr("destinations.id")`, the path `destination_id` uses today) | `D-DEST-PORTAL`, `D-DEST-ARRAY`, `D-DEST-SCOPE`. Same array shape and element order as `destination_id` and `destination_name`, including null elements. `id` is a string: P-DEST-2 `id_string_n` = 43241, `id_number_n` = 0. In `TABLE_SPECS` it sits directly after `destination_id` (`architecture.md` §8.4). Silver only. Backfill: `D-DEST-BACKFILL`. The P-DEST-1 check `id_eq_n` = 19799 shows that today's stored `destination_id` equals the `id` re-projection. On the 2 `sd_none_n` rows the projection gives an empty array, because P-DEST-2 `elem_null_n` = 0 and every element has a string `strapi_document_id`, so those rows have no elements. |
| `slv_enr_poi_destination` | `destination_name` | STRING | yes (unchanged) | `destinations.name` | `D-DEST-NAME`. No change. The backfill rewrites only the two id columns. P-DEST-1 `name_eq_n` = 19799. |
| `gld_srv_poi_info` | `destination_id` | STRING | yes (unchanged) | pipeline: `slv_enr_poi_destination.destination_id`. Init: `poi_master.destination_ids` (unchanged). | `D-DEST-GOLD`: still a 1-1 copy (`mapping_gld_srv_poi_info.md` §1.2), so pipeline values become `strapi_document_id`. `D-DEST-SCOPE`: no `destination_portal_id` on gold. `D-LEGACY-DEST`: the init mapping is not changed or rerun. `LEGACY_INIT` rows keep values outside the portal id space. P-LEGDEST-1: 24 distinct values, `in_portal_id` = 0, `in_strapi` = 1. P-LEGDEST-2: `LEGACY_INIT` has 34254 rows, 34167 with `destination_id`. |
| `gld_srv_poi_info` | `old_address` | STRING | yes (unchanged) | init: `ai_enriched_poi.address_line_2` (string). Pipeline: unchanged formula. | `D-MAP-OLD-ADDR`, `D-INIT-INFO-VI`, `D-INIT-ENRICH-ONLY`, `D-OLD-ADDR`. Taken from the `vi` row that `vi_key` selects. No matching source row gives NULL. |
| `gld_srv_poi_info` | `price_level` | INT | yes (unchanged) | init: `ai_enriched_poi.price_level` (int) | `D-MAP-PRICE-LEVEL`, `D-PRICE-TYPE`, `D-INIT-INFO-VI`, `D-INIT-ENRICH-ONLY`. int → INT, no cast. |
| `gld_srv_poi_info` | `price_min` | DECIMAL(18,2) | yes (unchanged) | init: `ai_enriched_poi.price_min` (int) | `D-MAP-PRICE-MIN`, `D-PRICE-TYPE`, `D-INIT-INFO-VI`, `D-INIT-ENRICH-ONLY`. Cast int → DECIMAL(18,2). |
| `gld_srv_poi_info` | `price_max` | DECIMAL(18,2) | yes (unchanged) | init: `ai_enriched_poi.price_max` (int) | `D-MAP-PRICE-MAX`, `D-PRICE-TYPE`, `D-INIT-INFO-VI`, `D-INIT-ENRICH-ONLY`. Cast int → DECIMAL(18,2). P-AI-1 `price_inverted_n` = 0. |
| `gld_srv_poi_multi_lang` | `story` | STRING | yes (unchanged) | init: `ai_enriched_poi.story` (string; 136321 of 136754 null) | `D-MAP-STORY`, `D-LANG-ROW`, `D-INIT-KEY`, `D-INIT-ENRICH-ONLY`. Match `(legacy_poi_id, lang)` through the map. A value is never copied to other langs. If the init has no row for the key, no row is created. |
| `gld_srv_poi_multi_lang` | `local_tips` | STRING | yes (unchanged) | init: `ai_enriched_poi.local_tips_or_neighborhood` (string) | `D-MAP-TIPS`, `D-LANG-ROW`, `D-INIT-KEY`, `D-INIT-ENRICH-ONLY`. Same key rule as `story`. The source has no column named `local_tips` (`ai_enriched_poi_schema.txt`). |

All six gold columns already exist with these types (`TABLE_SPECS` in `NB_SETUP_INITIAL_DDL`; `NEW_COLS` in `NB_CREATE_DDL` `oldpricepy`). There is no gold DDL change (`D-NO-GOLD-COL`), and the columns stay gold-only (`D-GOLD-ONLY`).

The init reads only these eight `ai_enriched_poi` columns: `poi_id`, `lang`, `address_line_2`, `price_level`, `price_min`, `price_max`, `story`, `local_tips_or_neighborhood`. It does not read the source's own `destination_id` or `destination_name` (`D-LEGACY-READ`, `D-LEGACY-DEST`).

## Lineage

**`slv_enr_poi_destination`**
- Bronze: `lh_vv_bronze.dbo.brz_enrichment_result`, `event_type = DESTINATION`, block `destinations`, parsed with an element schema that adds `strapi_document_id:string` next to `id` and `name` (`enr04` `DEST_ELEM_SCHEMA` and `ARRAY_PROJECTIONS`; `architecture.md` §8.1). The projections are:
  - `strapi_document_id` → `destination_id`;
  - `id` → `destination_portal_id`;
  - `name` → `destination_name`.
- All three use the existing `from_json` + `transform` + `to_json` path, which keeps element order and null elements (`NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md` §4).
- Registry: the destination rows change in both `init_cfg_enr` and `enrbrzcfgpy`, keyed `destination_id`, `destination_portal_id`, `destination_name` in that order (`architecture.md` §8.3).
- Backfill: existing rows are re-projected from their own producing bronze event (`D-DEST-BACKFILL`).
- Silver reads: none. Gold reads: none.

**`gld_srv_poi_info`**
- Pipeline (`NB_GLD_SRV_POI_INFO`): reads silver only.
  - `slv_enr_poi_destination.destination_id` is copied 1-1, and `destination_portal_id` is not selected (`D-DEST-SCOPE`).
  - The other inputs are unchanged: `slv_poi_entity_non_enrich`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review`, `slv_poi_media_info`, `slv_3p_poi_price`.
- Init (`lgpmain`, stage `info`):
  - Existing legacy reads: `poi_master`, `poi_detail`, `poi_rating`, `poi_review`, plus `gld_poi_legacy_id_map` through `vi_key`.
  - New legacy read: `ai_enriched_poi` (`address_line_2`, `price_level`, `price_min`, `price_max`), `lang = vi` row of `vi_key`, in the existing `OLD` catalog at a version pin.
  - The four values only fill rows that are already in `info_src`. No row is created from `ai_enriched_poi` alone (`D-INIT-ENRICH-ONLY`).

**`gld_srv_poi_multi_lang`**
- Pipeline (`NB_GLD_SRV_POI_MULTI_LANG`): reads silver only. Unchanged.
- Init (`lgpmain`, stage `multi_lang`):
  - Existing reads: `poi_enrichment_display`, `poi_master`, `gld_poi_legacy_id_map`.
  - New read: `ai_enriched_poi.story` and `local_tips_or_neighborhood`, matched on `(legacy_poi_id, lang)`.
  - The values only fill rows that are already in `ml_src`.

**Gold never reads gold.** Both pipeline notebooks read silver only. The init is a one-time job. It reads legacy gold in the `OLD` workspace and `gld_poi_legacy_id_map` and target `gld_srv_*` keys in the target workspace; that is existing `lgpmain` behaviour and not a pipeline gold-to-gold edge. No other legacy table is added (`D-LEGACY-READ`). `mapping_legacy_gold_to_gld_srv.md` line 157 still lists `ai_enriched_poi` under `Không đọc để nạp`, and that line changes with this task (`architecture.md` §10).

## Conflicts and questions

1. **Where the `D-LEGACY-DEST` note goes.** The ledger asks for a doc note: legacy-init `destination_id` values sit outside portal ids, and 1 of 24 distinct values is also a `strapi_document_id`. It does not name the file. The `LEGACY_INIT` source is described at `mapping_legacy_gold_to_gld_srv.md` §1 row 7, and the pipeline value at `mapping_gld_srv_poi_info.md` §1.1–§1.2. `architecture.md` §10 forbids naming the column `destination_portal_id` in `mapping_gld_srv_poi_info.md`. Recommendation: put the note on `mapping_legacy_gold_to_gld_srv.md` §1 row 7, and say "id portal" without the column name. Please confirm the file.
2. **`scope.files` in `task-state.yaml` is malformed.** The `D-G4` entries and two earlier test files are stored as one YAML string joined with ` - ` (lines 33–35), not as separate list items. The ledger row is clear, but tooling that reads `scope.files` will not see `tests/test_enr_extract_contract.py`, `tests/test_legacy_gold_poi_init_contract.py`, or `docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md` as separate files. Main should fix the list. This design does not edit it.
3. **Other reader of `slv_enr_poi_destination`.** `NB_SETUP_INITIAL_DDL` seeds the edge `slv_enr_poi_destination` → `gld_enr_poi_info` (`NB_ENR_POI_INFO`). That notebook is not in this read list. `architecture.md` §6 says it does not read the destination ids and asks the reviewer to confirm that it does not union silver by position. This design cannot confirm either point from the files it read.

Main merge, 2026-11-26: this file replaces the first `model-design.md`. Conflict 1 is closed by `D-LEGACY-DEST`: the note is on `mapping_legacy_gold_to_gld_srv.md` at the legacy-init `destination_id` row. Conflict 2 is closed: `scope.files` is a list of separate paths, including the two test files and `docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md`. Conflict 3 stays for the Architect to confirm from `NB_ENR_POI_INFO`, as round 1 §0 already stated that notebook does not read `destination_id`.
