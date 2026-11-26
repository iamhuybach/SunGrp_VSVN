# Model design: 20261125-practical-info-query-legacy-poi-id

## Scope

- Base task: `20261125-practical-info-query-legacy-poi-id` (`task-state.yaml`: status `triage`, signal `data_model_change`, system `poi-serving-api`).
- Design question: `sql/postgres/gld_srv_serve.pg.sql` (schema `apps`) and the entities under `services/data-serving-service` cannot turn a legacy `poi_id` into the new `poi_id`. This design gives the smallest gold and PostgreSQL shape that lets `/api/v1/pois/**` accept either id and return the same record that was already mapped.
- `proposal.md`, `problem-analysis.md` and `requirements-analysis.md` do not exist. No proposal section is implemented.
- `proposal.md` `## Dòng thay đổi`: Not applicable.
- `proposal.md` `## ctrl_cfg_schema_registry`: Not applicable.
- Ledger rows (`decision.md` `## Quyết định hiện hành`): D-ID-UNIT is cited only to exclude it. It limits how many `poi_id` values one request may carry (min 1, max 500). It is not a column, a value domain, a string length, or pagination `size`, so this design does not model it.
- This design does not use or change endpoint grain, `required_fields`, `source`, `poi_name`, `lang`, `page`, `size`, `sort_field` or `sort_order`. The Architect owns those.
- Approach: keep the gold map `lh_vv_gold.dbo.gld_poi_legacy_id_map` as it is and copy its key and resolution columns into one new read-only `apps` table. The API never recomputes `poi_id`.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_poi_legacy_id_map` | gold (Fabric, unchanged) | One row per legacy `poi_id` (`legacy_poi_id`). The legacy id is per language, so several rows can share one new `poi_id`. | DDL: `notebooks/NB_CREATE_DDL.ipynb` cell `legacyidpy` (`MAP_COLS`). Writer: `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb` cell `lgpmain`, stage `map` (insert-only on `legacy_poi_id`). |
| `apps.srv_poi_legacy_id_map` (proposed name, see Q1) | PostgreSQL serving (new) | Same as the gold map: one row per `legacy_poi_id` | No notebook. The repo has no job that writes `apps` (see Q4). DDL would go in `sql/postgres/gld_srv_serve.pg.sql`. |
| `apps.srv_poi_info` | PostgreSQL serving (unchanged) | One row per new `poi_id` | Unchanged. This is the lookup target of the resolved `poi_id`. |

Java side: one new read-only JPA entity for `apps.srv_poi_legacy_id_map` under `services/data-serving-service`, with `@Id` on `legacy_poi_id`. It has no `@IdClass` because the key has one column. It exposes only the columns listed below, as the service `AGENTS.md` `## Contract` requires.

## Keys

`lh_vv_gold.dbo.gld_poi_legacy_id_map` (unchanged):
- Primary key: `legacy_poi_id`. This is the MERGE key in `NB_SETUP_LEGACY_GOLD_POI` `lgpmain`, which calls `write_insert_only(MAP_FQ, map_src, ("legacy_poi_id",), ...)`. The same cell stops with an error if the source or the stored map has a duplicate `legacy_poi_id`. The table has no NodeSpec `pk` (see Q5).
- Business key: `legacy_poi_id`, the old `poi_master.poi_id` (per language). The silver name for this key is `ref_poi_legacy_id.legacy_poi_id` (`docs/context/01_DATA_MODEL.md` §6.1, §8). This design does not re-derive the old id formula.
- Resolved key: `poi_id`. The formula source is `docs/context/mapping_legacy_gold_to_gld_srv.md`, table under "`poi_id` mới không copy từ `poi_master.poi_id`" (`google` and `partner_portal` rows), implemented by `new_poi_id` in `lgppure`. This design adds no second formula.
- Foreign key (logical only): `poi_id` → `gld_srv_poi_info.poi_id`, valid only when `poi_id_status = 'OK'` (as `lgpmain` builds it with `mp = map_rows.where("poi_id_status = 'OK'")`).

`apps.srv_poi_legacy_id_map` (new):
- Primary key: `legacy_poi_id`, copied from the gold map key above.
- Business key: `legacy_poi_id`.
- Foreign key (logical only, no constraint): `poi_id` → `apps.srv_poi_info.poi_id`. `gld_srv_serve.pg.sql` creates no FK, index, or view, and this design adds none.

`apps.srv_poi_info` (unchanged): primary key `poi_id` (service `AGENTS.md` `## Contract`, `gld_srv_serve.pg.sql`).

## Columns

The type mapping is the `gld_srv_serve.pg.sql` header rule `STRING -> text`. NOT NULL appears only where the gold column is NOT NULL in `MAP_COLS`.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `apps.srv_poi_legacy_id_map` | `legacy_poi_id` | `text` | NOT NULL | `gld_poi_legacy_id_map.legacy_poi_id` (`MAP_COLS`: STRING NOT NULL) | Copied unchanged. Primary key. This is the value the API matches when it receives a legacy id. Source: author input "Map columns already declared" and `lgpmain` key. |
| `apps.srv_poi_legacy_id_map` | `poi_id` | `text` | NULL | `gld_poi_legacy_id_map.poi_id` (`MAP_COLS`: STRING) | Copied unchanged. The API uses this value to read `apps.srv_poi_*`. It is never recomputed in the API (author input rule "Do not recompute `poi_id` in the API"). The formula is in `mapping_legacy_gold_to_gld_srv.md`. |
| `apps.srv_poi_legacy_id_map` | `poi_id_status` | `text` | NOT NULL | `gld_poi_legacy_id_map.poi_id_status` (`MAP_COLS`: STRING NOT NULL) | Copied unchanged. Only rows with `poi_id_status = 'OK'` resolve, the same rule `lgpmain` uses to build gold rows. Rows marked `MISSING_EVIDENCE` have `poi_id` NULL and do not resolve. |
| `apps.srv_poi_legacy_id_map` | `ingestion_ts` | `timestamp without time zone` | NULL | None in gold | Present on every `apps` table under the `gld_srv_serve.pg.sql` header exception. Whether it applies to this table is open (Q3). |

The gold map's other columns are not exposed in this minimum shape: `lang`, `legacy_ingestion_source`, `source_id` and `source_name` (see Q6). No column is added to `gld_poi_legacy_id_map` or to the five existing `apps.srv_poi_*` tables.

## Lineage

`lh_vv_gold.dbo.gld_poi_legacy_id_map` (existing, unchanged):
- Bronze: none.
- Silver: none in the current writer. `01_DATA_MODEL.md` §6.1 names a silver equivalent, `ref_poi_legacy_id` (key `legacy_poi_id`), but the map does not read it (see Q2).
- Gold: `lgpmain` reads the legacy gold `sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master` at a pinned Delta version. This is a one-time init from legacy gold into new gold (`mapping_legacy_gold_to_gld_srv.md` intro). It conflicts with the rule that gold never reads gold (Q2).

`apps.srv_poi_legacy_id_map` (new):
- Bronze: none. Silver: none.
- Gold: `lh_vv_gold.dbo.gld_poi_legacy_id_map` only, copied one row per row. This is a gold-to-serving copy, not a new gold table, so no gold table reads another gold table.

`apps.srv_poi_info` and the other `apps.srv_poi_*` tables: lineage unchanged. They are only looked up by the resolved `poi_id`.

API read path: incoming id → `apps.srv_poi_legacy_id_map` (`legacy_poi_id`, `poi_id_status = 'OK'`) → `poi_id` → existing `apps.srv_poi_*` reads. Only schema `apps` is read.

## Conflicts and questions

1. Table name. `gld_poi_legacy_id_map` does not follow the `gld_srv_<chủ đề>_<grain>` serving pattern in `02_NAMING_CONVENTION.md`, and the service `AGENTS.md` scope is `apps.srv_poi_*` derived from `gld_srv_poi_*`. Confirm the name `apps.srv_poi_legacy_id_map` and that a `gld_*` table outside `gld_srv_*` may be mirrored into `apps`. The service `AGENTS.md` `## Contract` and `tests/test_srv_poi_serving_contract.py` currently allow only the five `gld_srv_poi_*` sources.
2. Gold reads gold, and the silver source is not used. The map is built from legacy gold `poi_master`, not from silver `ref_poi_legacy_id` (§6.1) or `slv_poi_source_map.legacy_poi_ids_json` (§6, N1). This design keeps the existing map as the single source, as the author input instructs. Should a later task move the map's lineage onto silver?
3. `ingestion_ts`. The `gld_srv_serve.pg.sql` header puts it on "mọi bảng apps" (every `apps` table), and the repo has no job that writes it. Should the new table also have it?
4. Who copies the data. No repo job writes `apps` tables. How the gold map reaches `apps.srv_poi_legacy_id_map` (full copy or `OK` rows only) is a data-movement decision for the Architect. It is not modelled here.
5. Key source. The header of `gld_srv_serve.pg.sql` says primary keys come from NodeSpec `pk`. The map has no NodeSpec, so `legacy_poi_id` comes from the `lgpmain` MERGE key. Confirm this exception is acceptable.
6. Extra map columns. Should `lang`, `legacy_ingestion_source`, `source_id` or `source_name` also be exposed? They exist in `MAP_COLS` but resolution does not need them. Exposing `lang` would also bear on whether a legacy id's language affects the response, which the Architect owns.
7. Both id kinds in one request. No file says whether the two id formats can overlap. A request value might match both an `apps.srv_poi_info.poi_id` and an `apps.srv_poi_legacy_id_map.legacy_poi_id`. What order and tie rule should apply? This is for the Architect; the design adds no column for it.
8. Unresolved legacy ids. When a legacy id has `poi_id_status` other than `OK`, or has no map row, what should the API return? This is API contract, not data model.
9. Many legacy ids to one `poi_id`. A request may send several legacy ids (one per old language) that resolve to the same `poi_id`. Whether the response is deduplicated is an endpoint-grain decision for the Architect.
