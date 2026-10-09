RESULT: PASS

# Architecture — Redesign 3P silver L1 to the raw crawl payload

Task: `20261009-redesign-3p-silver-raw-payload`
Architect: Cursor subagent `claude-opus-5-5-medium` (approved model-policy exception, see `task-state.yaml`).
Inputs read: `task-state.yaml`, `request.md`, `decision.md`, `evidence/e1-interpretation.md`, `evidence/results/e1_3p_payload_shape.txt`, `evidence/results/e1b_3p_block_schemas.txt`, `evidence/l1-block-comparison.md`, `evidence/sample-key-tree.md`, `evidence/plan.md`, `docs/context/01_DATA_MODEL.md` §4–§8, `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `docs/context/CTRL_TABLES_CONTEXT.md` §2–§5, `docs/context/NB_00_ORCHES_SLV_TO_GLD.md` §1, `notebooks/NB_CREATE_DDL.ipynb` (`TABLE_CONFIGS_3P`, `seed_registry`, 3P `ctrl_mng_pipeline_config` seed), `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` (all cells), `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` (`build_table_specs`, `load_table_specs`, `snapshot_path_error`, `ensure_target`, `run_merge`, `load_state`, `commit_state`, `merge_rejects`, `finalize_watermark`, `run_controlled`, `RunContext.updates_watermark`), `scripts/vv.py` (`cmd_verify`).

No payload values or personal data are reproduced here. Paths, JSON types, counts, and identifiers only.

## 1. Context and scope

The 3rd-party collector now emits a raw `normalized_payload` without the LLM enrichment blocks. Probe E1 scanned the whole current `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` (33 documents). Locked population facts for that table:

| Fact | Value |
|---|---|
| `extra_info` | empty object on 33/33; `enrichment`, `enrichmentSiblings`, `enrichmentFailedLangs` present on 0 |
| `poi_content`, `poi_price`, `policies`, `raw_data` non-null | 0 each |
| `poi_amenity` key set | exactly `amenity_schema`, `ext_attributes` on 33/33; 38 flat flag names present on 0 |
| `poi_review`, `poi_media` | array on 33/33; 165 elements each; 0 missing key parts; 0 duplicate key groups |
| `ext_attributes` merged schema | union of keys across rows; not a per-row guarantee |

The user decided (2026-10-09, `decision.md` and the gate request) that L1 is a 1:1 structural extract with type casts, technical snapshot columns, and the existing derived MERGE keys. Every transform with its own logic belongs to silver L2.

### 1.1 In scope

- `notebooks/NB_CREATE_DDL.ipynb`: `TABLE_CONFIGS_3P`, the 3P registry seed comment, the 3P `ctrl_mng_pipeline_config` seed, and one new idempotent deactivation cell.
- `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`: remove the language contract, narrow accepted load modes, add drift observability.
- `docs/context/01_DATA_MODEL.md` §5.2 and §6, `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `docs/context/CTRL_TABLES_CONTEXT.md` §3 and §5 (3P parts).
- A new deterministic local test `tests/test_3p_l1_contract.py`.
- The input contract for L2 nodes N2 `slv_poi` and N4 `slv_poi_localization`, and the read restrictions for N1, N3, N5.

### 1.2 Sample key tree (block level)

Full path/type tree: `evidence/sample-key-tree.md` (one document) and `docs/context/01_DATA_MODEL.md` §4. Block-level summary with E1 population status:

| Top-level path | JSON type (sample) | E1 population | L1 consumer after this change |
|---|---|---|---|
| root scalars: `source_id`, `source`, `poi_name`, `poi_name_normalized`, `business_sector`, `business_category`, `operating_status`, `country_code`, `language_code`, `created_at`, `poi_id` | string | not counted | `slv_3p_poi` (subset, see §4.2) |
| root nullables: `partner_id`, `slug`, `slug_history`, `price_level`, `star_rating`, `accommodation_type`, `awards`, `poi_amenity_schema` | null | not counted | `slv_3p_poi` (subset, several already inactive) |
| `subcategory_tags`, `types` | array of string | not counted | `slv_3p_poi` JSON columns |
| `facilities` | object | not counted | `slv_3p_poi.facilities_json` |
| `poi_address` | object | not counted | `slv_3p_poi_address` |
| `poi_contact` | object | not counted | `slv_3p_poi_contact` |
| `poi_rating` | object | not counted | `slv_3p_poi_rating` |
| `poi_opening_hours` | object | not counted | `slv_3p_poi_opening_hours` |
| `poi_amenity` | object {`amenity_schema`, `ext_attributes`} | 33/33 exactly these keys | `slv_3p_poi_amenity` |
| `poi_review` | array of object | array 33/33 | `slv_3p_poi_review` |
| `poi_media` | array of object | array 33/33 | `slv_3p_poi_media` |
| `poi_price`, `poi_content`, `policies` | null | non-null 0 | none (tables inactive) |
| `extra_info` | object, no children | empty 33/33 | none (watched only, §9) |
| `raw_data` | absent | non-null 0 | none (table inactive) |

## 2. Non-goals

- Partner CDC (`partner_raw_data`, `slv_pn_*`, `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`). No N2/N4 partner column contract changes, so partner stays out.
- `NB_LIB_EXTRACT_RAWDATA` is not modified. The shared lib keeps generic `LANG` / `LANG_ARRAY` support. The 3P notebook narrows what it accepts.
- No change to `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. No 3P activity.
- No new L1 table. No `DROP TABLE`, no `ALTER TABLE ... DROP COLUMN`, no delete of silver rows.
- No reading of bronze `raw_payload`.
- No new projection of payload fields beyond `poi_opening_hours.open_now`. Fields that the registry already omits on purpose (`poi_address.address_google`, root `source`, root `country_code`, root `price_level`) stay omitted. Omitting a field is not a business rule and does not block this task.
- Implementing the N2/N4 node notebooks. They are not in the repository (§11.5).
- Gold: no new business rule, no change.
- Renaming bronze or moving control tables (task `20261008-migrate-ctrl-lakehouse-rename-3p-raw`).

## 3. Invariants

| ID | Invariant |
|---|---|
| INV-1 | Every active L1 column `json_path` is either a technical prefix (`_doc.<raw column>`, `_pos`, `$`) or a path present in the confirmed key tree of §1.2. No active path starts with `extra_info`, and no active path uses `_lang`, `_langs`, or `_align`. |
| INV-2 | The 3P extract accepts only `load_mode` in (`DOC`, `DOC_ARRAY`). An active 3P table with any other mode fails with `ConfigError` before the lock is taken and before any write. |
| INV-3 | `poi_id = HASH_MD5_UUID(_doc.source_name, _doc.source_id)` on every 3P L1 table. Payload `poi_id` is stored only as `slv_3p_poi.collector_poi_id`. `review_id = HASH_SHA256(_doc.source_name, _doc.source_id, author_name, time)`. `media_dedup_key = HASH_SHA256_PIPE(_doc.source_name, _doc.source_id, photo_api_uri)`. Formulas are unchanged. |
| INV-4 | Event order is (`crawled_at`, `event_id`). A row in a target table is updated only when the incoming order is ≥ the stored (`_crawled_at`, `_event_id`). State rows never move backward (`STATE_NOT_OLDER`). |
| INV-5 | `wm_transform_brz_3rd_crawler_poi_stream` advances only on an incremental run (not `dry_run`, not `full_reload`, empty `table_filter`) whose status is `SUCCESS` or `NO_DATA`, only while the run holds the lock, and never backward (`finalize_watermark`). `PARTIAL_FAILED` / `FAILED` never advance it. |
| INV-6 | A DOC block that is JSON null or absent produces no row for that document, so the stored row is not NULL-overwritten. A DOC_ARRAY that is null, empty, or not an array produces no rows. Inside a present block or the root document, a missing field writes NULL (snapshot semantics, unchanged). |
| INV-7 | The extract never deletes. Child tables upsert only; `_last_seen_at` records the last crawl that carried the element. |
| INV-8 | Deactivated L1 tables and dropped columns are frozen: no writer touches them after the change. Their historical rows stay readable. No L2 edge or node may read them (§11). |
| INV-9 | L1 applies no language filter, builds no localization object, maps no amenity flag, and chooses no canonical name, description, sector, category, slug, or destination. |
| INV-10 | The reject reasons and their precedence are unchanged: `MISSING_ENTITY_KEY` (blank `source_name` / `source_id`), `OUT_OF_SCOPE` (ignored, not rejected), `INVALID_PAYLOAD` (blank or non-object payload), `MISSING_EVENT_ORDER` (null `crawled_at`). Element-level rejects keep `INVALID_PAYLOAD` / `MISSING_ENTITY_KEY`. |
| INV-11 | The extract does not read gold and does not read `raw_payload`. |

## 4. State ownership, grain, and keys

### 4.1 Ownership

| State | Owner (writer) | Readers |
|---|---|---|
| `ctrl_cfg_schema_registry` rows for `src_tbl = brz_3rd_crawler_poi_stream` | `NB_CREATE_DDL` seed cell (`seed_registry`, `replaceWhere` on the 3P source only) | 3P extract |
| `ctrl_mng_pipeline_config` 3P extract rows | `NB_CREATE_DDL` seed (insert-if-missing) plus the new deactivation cell | 3P extract |
| `ctrl_mng_watermark` row `wm_transform_brz_3rd_crawler_poi_stream` (pointer and lock) | 3P extract via lib `acquire_lock` / `finalize_watermark` / `release_lock` | 3P extract, operators |
| `ctrl_cdc_state` partition `src_tbl = brz_3rd_crawler_poi_stream` | 3P extract `commit_state` | 3P extract |
| `ctrl_cdc_reject` partition `src_tbl = brz_3rd_crawler_poi_stream` | 3P extract `merge_rejects` | operators |
| `ctrl_log_run`, `ctrl_log_table_run` (3P rows) | 3P extract | operators, `NB_00_ORCHES_SLV_TO_GLD` batch pinning |
| `lh_vv_silver.dbo.slv_3p_poi_*` (8 active tables) | 3P extract MERGE | L2 nodes |
| 5 deactivated tables + `slv_3p_poi_policy` | none (frozen) | none after the L2 contract change |
| `slv_poi*` L2 tables | L2 node notebooks (not in repo) | gold nodes |

### 4.2 Active L1 tables after the change

Grain and keys are unchanged for every table that stays active. Registry totals: 9 tables, 93 columns (78 active, 15 inactive). Pipeline config: 8 active tables, 6 inactive.

| Table | load_mode | `src_object` | Grain | MERGE key | Columns total (active) before → after | Column changes |
|---|---|---|---|---|---|---|
| `slv_3p_poi` | DOC | `$` | 1 row / `poi_id` | `poi_id` | 23 (17) → 21 (15) | remove `available_langs_json` (`_langs`), remove `enrichment_failed_langs_json` (`extra_info.enrichmentFailedLangs`) |
| `slv_3p_poi_address` | DOC | `poi_address` | 1 / `poi_id` | `poi_id` | 21 (20) → 21 (20) | none |
| `slv_3p_poi_contact` | DOC | `poi_contact` | 1 / `poi_id` | `poi_id` | 8 (5) → 8 (5) | none |
| `slv_3p_poi_opening_hours` | DOC | `poi_opening_hours` | 1 / `poi_id` | `poi_id` | 6 (6) → 7 (7) | add `open_now` BOOLEAN, path `open_now`, rule `NONE`, appended last |
| `slv_3p_poi_rating` | DOC | `poi_rating` | 1 / `poi_id` | `poi_id` | 5 (3) → 5 (3) | none |
| `slv_3p_poi_amenity` | DOC | `poi_amenity` | 1 / `poi_id` | `poi_id` | 41 (29) → 3 (3) | keep `poi_id`, `amenity_schema_json` (`amenity_schema`), `ext_attributes_json` (`ext_attributes`); remove the 38 flag columns |
| `slv_3p_poi_review` | DOC_ARRAY | `poi_review` | 1 / review element | `review_id` | 8 (8) → 8 (8) | none |
| `slv_3p_poi_media` | DOC_ARRAY | `poi_media` | 1 / media element | `media_dedup_key` | 18 (15) → 18 (15) | none; `dedup_order` stays `display_order ASC, media_id ASC` |
| `slv_3p_poi_policy` | DOC | `policies` | — | `poi_id` | 2 (2) → 2 (2) | registry kept; pipeline config stays `is_active = 0` |

Removed from `TABLE_CONFIGS_3P` and deactivated in pipeline config: `slv_3p_poi_price`, `slv_3p_poi_raw_data`, `slv_3p_poi_content`, `slv_3p_poi_enrichment`, `slv_3p_poi_review_i18n` (50 registry columns).

Technical columns on every active table, unchanged: `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `_ingested_at` (`SNAPSHOT_TECH_COLUMNS`).

`slv_3p_poi.language_code` keeps `_doc.language_code` with `LOWER_TRIM`. That is existing type normalization of the document language key, not language filtering.

### 4.3 L1 old/new comparison

| L1 table | Before | After | Reason (evidence) |
|---|---|---|---|
| `slv_3p_poi` | DOC `$`, 17 active | DOC `$`, 15 active | `enrichmentFailedLangs` absent (E1 = 0); `_langs` derived from enrichment is not 1:1 |
| `slv_3p_poi_address` | active | active, unchanged | structural |
| `slv_3p_poi_contact` | active | active, unchanged | structural |
| `slv_3p_poi_opening_hours` | active, `open_now` not projected (old D3) | active, `open_now` added | user decision; field exists in sample key tree |
| `slv_3p_poi_rating` | active | active, unchanged | structural |
| `slv_3p_poi_amenity` | 29 active incl. 26 flags | 3 active | `amenity_flat_flag_docs` = 0; mapping `ext_attributes` onto flags is L2 logic |
| `slv_3p_poi_review` | active | active, unchanged | arrays 33/33, key gaps 0, dup groups 0 |
| `slv_3p_poi_media` | active | active, unchanged | arrays 33/33, key gaps 0, dup groups 0 |
| `slv_3p_poi_price` | active | inactive, registry removed | `poi_price_nonnull` = 0 |
| `slv_3p_poi_raw_data` | active | inactive, registry removed | `raw_data_nonnull` = 0; do not switch to `raw_payload` |
| `slv_3p_poi_content` | active | inactive, registry removed | `poi_content_nonnull` = 0 |
| `slv_3p_poi_enrichment` | active LANG | inactive, registry removed | enrichment paths 0 |
| `slv_3p_poi_review_i18n` | active LANG_ARRAY | inactive, registry removed | enrichment paths 0 |
| `slv_3p_poi_policy` | inactive | inactive, unchanged | `policies_nonnull` = 0 |

### 4.4 Extract-to-L2 behavior list

Stays in extract (structural):

- Parse `normalized_payload` once as a JSON object; classify VALID / IGNORED / REJECTED with the INV-10 rules.
- Explode a present DOC block to one row and a DOC_ARRAY to one row per element (`posexplode`).
- Cast registry types; enforce `cast_null_policy`.
- Derived MERGE keys `poi_id`, `review_id`, `media_dedup_key` (INV-3).
- Technical snapshot columns.
- Skip an absent block (INV-6); order by (`crawled_at`, `event_id`) (INV-4); `sources` scope filter (`OUT_OF_SCOPE`, unchanged).
- Drift counters (§9), which observe the payload and never change data.

Leaves extract, now owned by L2:

| Behavior | Former L1 mechanism | New owner / state |
|---|---|---|
| Language allow-list and fallback | `langs`, LANG / LANG_ARRAY | N4 via `ref_lang_policy` |
| Localization objects | `lang_object_path`, `lang_map_path`, `lang_field`, `lang_entries` | removed; no source |
| Document language set | `available_langs_json` from `_langs` | N4 aggregates real-name languages (already the gold `available_langs` source) |
| Enrichment failure map | `enrichment_failed_langs_json` | removed; no source |
| Amenity flags | 38 flat columns | L2 may later derive from `slv_3p_poi_amenity.ext_attributes_json` / `amenity_schema_json`; not in this task |
| Canonical name / description | `slv_3p_poi_enrichment`, `slv_3p_poi_content` | N4 contract §11.3 |
| Sector / category / type / tags / brand / model | `slv_3p_poi_enrichment` + `slv_3p_poi` | N2 contract §11.2 |
| Slug, destination | already L2 (N4, N5) | unchanged |

## 5. Ordering and transaction boundaries

One incremental or `full_reload` run, in order (unchanged lib flow; only the active table set and the language steps change):

1. `build_context` validates parameters. `load_table_specs(ctx, EXTRACT_MODES)` and `check_config` validate configuration. Failure means `ConfigError` with no lock and no write.
2. `load_watermark`; `run_controlled` acquires the lock on `wm_transform_brz_3rd_crawler_poi_stream` (not in `dry_run`). Losing the race means `SKIPPED_CONCURRENT`.
3. `ctrl_log_run` RUNNING row; `pin_snapshot` fixes `src_version_to`.
4. Read raw (VERSION, or FULL for `full_reload` / gap with `allow_full_scan`), classify, profile, drift counters.
5. Load state (skipped for `full_reload`).
6. One wave over 8 tables (priority 1, `max_parallel` 12). Per table: `ensure_target` (may `ALTER TABLE ADD COLUMNS open_now` once) → build rows → stats → cast-null gate → `resolve_latest` → one Delta MERGE (atomic per table) → lazy state rows.
7. `decide_status`.
8. `commit`: one MERGE into `ctrl_cdc_state` for SUCCESS tables → one MERGE into `ctrl_cdc_reject` (document rejects plus element rejects of SUCCESS tables) → append `ctrl_log_table_run`.
9. `finalize_watermark` (INV-5) → final `ctrl_log_run` → `release_lock` (`finally`, only own lock).

Commit boundaries: each silver MERGE, the state MERGE, the reject MERGE, the table-log append, the watermark update, and the run-log append are separate Delta commits. There is no cross-table transaction. Correctness relies on the ordering above plus idempotent re-application (§6).

Configuration change boundary (rollout, §10): the pipeline-config deactivation `UPDATE` and the registry reseed are two separate commits. Either order is safe:

| State between commits | Old notebook | New notebook |
|---|---|---|
| Config deactivated, registry old | runs 8 tables with old columns (enrichment columns would read absent paths → NULL) | runs 8 tables; old `_langs` / `extra_info` rows still active → `check_config` `ConfigError`, no write |
| Registry new, config old | LANG tables have no active registry rows → `ConfigError`, no write | LANG tables active → `ConfigError` (INV-2), no write |

To make the window empty, apply both config commits while no 3P run holds the lock, then deploy the notebook (§10.2).

## 6. Idempotency, concurrency, and recovery

### 6.1 Idempotency

- Re-reading the same document: `resolve_latest` keeps one row per key; the MERGE guard (INV-4) updates on equal order with identical values, so the result is unchanged except `_ingested_at`. L2 recomputes by `row_hash`, so equal content creates no downstream change.
- Incremental re-read after a crash: state filters documents already applied for SUCCESS tables; failed tables have no state and are re-applied.
- `full_reload`: state is ignored and every document is re-applied under the MERGE guard. Equal-order rows are rewritten. Older documents cannot overwrite newer rows. The state MERGE (`>=`) rewrites `last_run_id` / `src_version` only.
- Rejects: `event_hash` identity; a re-read increments `reject_count` and inserts no duplicate.
- `ensure_target`: `ADD COLUMNS` only when the column is missing, so it runs once.
- Deactivation cell: `UPDATE ... WHERE ... AND is_active <> 0` is a no-op on rerun. `seed_registry` uses `replaceWhere` on the 3P source and is idempotent.

### 6.2 The required rerun is `full_reload`

The 33 current documents were already processed by the old extract, so `ctrl_cdc_state` holds their `poi_id` with their (`crawled_at`, `event_id`). An incremental run would mark every one stale and never write `open_now`. The first run under the new code must therefore use `full_reload = True`, `allow_full_scan = True`, `table_filter = ""`. It does not move the watermark (`RunContext.updates_watermark` is false for `full_reload`). It still takes the watermark lock, so it cannot overlap an incremental run.

### 6.3 Concurrency

| Pair | Protection |
|---|---|
| 3P run vs 3P run (incremental or `full_reload`) | Lock on the watermark row; the second run gets `SKIPPED_CONCURRENT` |
| 3P `dry_run` vs anything | `dry_run` takes no lock and writes nothing (`ensure_target` does not ALTER in `dry_run`) |
| 3P vs partner extract | `ctrl_cdc_state` / `ctrl_cdc_reject` MERGEs are scoped to the `src_tbl` partition; silver targets are disjoint |
| 3P extract vs `NB_00_ORCHES_SLV_TO_GLD` | L2 reads committed Delta versions and pins the last completed extract batch from `ctrl_log_run`; per-table MERGE commits are atomic |
| Registry reseed vs running 3P run | Specs load before the lock; a run that loaded specs before the reseed finishes with old specs. Rollout requires no lock holder during the change (§10.2) |
| Parallel tables within a run | One writer per target table (`run_merge` contract); 8 tables ≤ `max_parallel` 12, so there is one wave |

### 6.4 Retry and recovery

- Transient Delta conflict inside a table: `process_with_retry` with `max_retries`.
- Table FAILED (including `CastNullError`): no state for that table; run `PARTIAL_FAILED`; watermark kept; the notebook raises. Recovery: fix the cause and rerun. Under rollout use `full_reload = True` with `table_filter = <failed tables>`. In steady state use a normal incremental run.
- Crash after a silver MERGE and before the state MERGE: re-apply is idempotent (§6.1).
- Crash after the state MERGE and before the watermark update: the next incremental run re-reads the range; state marks the applied documents stale; rejects re-merge by `event_hash`.
- Lost lock (run exceeded `running_timeout_minutes`): `finalize_watermark` refuses to write and reports it in `error_message`.

## 7. Partial-failure behavior

| Failure point | Silver | State | Watermark | Next action |
|---|---|---|---|---|
| `ConfigError` (mode, `_langs`/`_lang`/`extra_info` path, missing doc key, missing raw column) | untouched | untouched | untouched, no lock | fix config |
| Classification or read error | untouched | untouched | FAILED, not advanced | rerun |
| Subset of tables FAILED | SUCCESS tables committed | SUCCESS tables only | not advanced | rerun failed tables |
| Commit phase error after MERGEs | committed | maybe partial | not advanced (status FAILED) | rerun; idempotent |
| Watermark write error | committed | committed | not advanced | rerun; state skips applied documents |
| Drift counters non-zero (§9) | normal | normal | normal | WARN only; operator decision (§10.5) |

`stop_on_failure` has no effect with one wave.

## 8. Alternatives and trade-offs

Only decisions with a real remaining trade-off are listed. Everything else is locked by the user decisions.

| # | Decision | Options | Selected | Reason |
|---|---|---|---|---|
| A1 | Registry rows of the 5 deactivated tables | (a) keep them in `TABLE_CONFIGS_3P`, inert behind `pipeline_config.is_active = 0`, like policy; (b) remove them | (b) | Keeps the registry equal to the confirmed active contract (acceptance criterion). Enrichment and review_i18n rows carry `_lang` / `_align` / enrichment paths that no longer exist. Accidental reactivation fails fast (`chưa có cột active trong ctrl_cfg_schema_registry` or INV-2) instead of silently running. Rollback restores them from Git (§10.4). Policy stays as is, because the user asked to keep it unchanged. |
| A2 | Dropped columns (38 amenity flags, `available_langs_json`, `enrichment_failed_langs_json`) | (a) remove from registry, leave physical columns frozen; (b) `ALTER TABLE DROP COLUMN`; (c) `UPDATE ... SET NULL` | (a) | (b) needs column mapping, cannot be rolled back with a reseed, and counts as destructive DDL. (c) rewrites historical rows that the user wants kept. With (a), new inserts get NULL and updated rows keep their last historical value. This is acceptable only because INV-8 forbids L2 from reading these columns. |
| A3 | `available_langs_json` | (a) keep, derived from `language_code` only; (b) remove | (b) | (a) would be a single-element copy of `language_code`, which is a derivation, not 1:1. The gold `available_langs` already comes from N4. |
| A4 | Language code in the 3P notebook | (a) keep it dormant (`langs = ""`, paths unused); (b) delete it and accept only `DOC` / `DOC_ARRAY` | (b) | Dormant parameters could be re-pointed at absent paths and recreate L1 business logic. Deletion plus INV-2 makes the boundary enforceable. The lib keeps generic support, so partner and future sources are unaffected. |
| A5 | Detecting the return of enrichment or of null blocks | (a) silent; (b) counters in the exit JSON and logs | (b) | After this change L1 no longer parses `extra_info`, `poi_content`, `poi_price`, `policies`, or `raw_data`. Without counters, a collector change would drop data silently. The counters read the already-parsed payload and never change status. |
| A6 | First rerun | (a) `full_reload`; (b) reset state or watermark | (a) | Locked by the user. (b) touches the watermark and the state of every document. |

## 9. Selected design — extract notebook changes

All changes are in `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`. Source comments are in Vietnamese and follow the existing `[SỬA 09/10]` / `[BỎ 09/10]` / `[THÊM 09/10]` markers.

1. Parameters cell: remove `langs`, `lang_object_path`, `lang_field`, `lang_map_path`. `lang_field` goes too because it only qualifies `lang_object_path`. Update the `max_parallel` comment to "8 bảng active cùng 1 wave". Keep every other parameter and default.
2. Constants: remove `ENTRY_TYPE` and `LANG_MODES`. Set `ARRAY_MODES = ("DOC_ARRAY",)`. Add `EXTRACT_MODES = ("DOC", "DOC_ARRAY")`. Keep `RAW_LANG = "language_code"`, used only in `doc_columns` and the reject `source_payload`. Update its markdown row so it is no longer "gộp vào `_langs`". Add:
   - `FORBIDDEN_PATH_HEADS = ("_lang", "_langs", "_align", "extra_info")`.
   - `WATCH_BLOCKS = ("poi_content", "poi_price", "policies", "raw_data")`, top-level blocks of deactivated or inactive tables.
   - `WATCH_EMPTY_OBJECT = "extra_info"`.
   - `KNOWN_TOP_KEYS`: the 34 top-level keys of §1.2 (the 33 sample keys plus `raw_data`). Key names only.
3. Remove `lang_entries()` and `uses_langs()`. Remove the `need_langs` parameter from `top_fields`, `classify_docs`, and `profile_docs`, and from the `process_run` call sites.
4. `classify_docs`: delete the language block (`_le_all`, `_primary_no_lang`, `_langs_arr`, `_langs`, `_lang_entries`). Add drift flags computed from the raw payload string before `_payload` is nulled, VALID only, as booleans (no block text is cached):
   - `_w__<block>` = `get_json_object(_payload, '$.<block>') IS NOT NULL` for each `WATCH_BLOCKS` entry.
   - `_w__extra_info_nonempty` = `size(json_object_keys(get_json_object(_payload, '$.extra_info'))) > 0` (null-safe, `coalesce` to false).
   - `_w__unknown_keys` = `array_except(json_object_keys(_payload), array(<KNOWN_TOP_KEYS>))`.
5. `presence`: remove the LANG branch. `expand_rows`: remove the LANG / LANG_ARRAY branch. An unexpected mode raises `ConfigError`, which load-time validation already prevents. Keep `align_path` handling for DOC_ARRAY: it is generic positional alignment and is unused by current config.
6. `part_value`: remove the `_lang` and `_langs` branches. `check_config` enforces the restriction.
7. `profile_docs`: remove `lang_stats`. Add one aggregate pass over VALID rows for the counters of step 4. Return `watch = {"inactive_blocks": {block: docs>0 only}, "extra_info_nonempty": n, "unknown_top_keys": {key: docs}}`. The keys come from `explode(_w__unknown_keys)` grouped. Key names only, never values.
8. `process_run`: replace `out.extra["langs"]` with `out.extra["watch"]`. Log a WARN when any watch counter is non-zero. Keep `docs_by_table` and `bad_shape`. Watch counters never change `out.status`.
9. `build_context`: remove the lang path and `lang_field` validation and remove the four keys from `params` / `run_params`.
10. `check_config`: add two errors, both raised before the lock:
    - any active column whose any `paths` head (split on `.`) is in `FORBIDDEN_PATH_HEADS`;
    - any spec whose `load_mode` is not in `EXTRACT_MODES`. This is defense in depth; `load_table_specs(ctx, EXTRACT_MODES)` already rejects it.
11. `run_extract`: call `load_table_specs(ctx, EXTRACT_MODES)`.
12. Markdown cells (header table, constants table, function tables, State table, Vận hành table, Bảng đích table): remove LANG / LANG_ARRAY, `langs`, enrichment and review_i18n rows. List the 8 active tables. Document the frozen tables and columns and the `watch` exit key. Replace the "Thêm ngôn ngữ" row with: "Ngôn ngữ do L2 (`ref_lang_policy`) quyết định".

Exit JSON contract: the key `langs` is removed and the key `watch` is added. `status` values and the raise-on-`FAILED` / `PARTIAL_FAILED` / `SKIPPED_CONCURRENT` behavior are unchanged. No pipeline in the repository consumes this notebook's exit value (grep of `pipelines/`: no 3P reference).

## 10. Rollout, rollback, and forward recovery

### 10.1 Pre-change snapshot (Fabric DEV, recorded in the runtime runbook)

- `DESCRIBE HISTORY` latest version of `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry`, `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`, and the 8 active plus 5 deactivated `slv_3p_poi_*` tables.
- The watermark row (`last_src_version`, `last_src_table_id`, `watermark_value`, `status`, `lock_exec_id`).
- 3P counts by `trg_tbl` from `ctrl_cdc_state` and `ctrl_cdc_reject` (unresolved).
- Row counts of every `slv_3p_poi_*` table.

### 10.2 Apply

1. Confirm `lock_exec_id IS NULL` on `wm_transform_brz_3rd_crawler_poi_stream` and that no 3P run is scheduled.
2. Run the new deactivation cell in `NB_CREATE_DDL`, then verify that 8 active and 6 inactive 3P rows exist.
3. Run the 3P registry seed cell and `show_registry`. Expect 9 tables and 93 columns (15 inactive).
4. Deploy the updated extract notebook.
5. `dry_run = True, full_reload = True, allow_full_scan = True`. Expect no `ConfigError`, 8 table results, `cast_null` empty (in particular `open_now`), `watch` all zero, and `docs_by_table` with 33 for each DOC table whose block is present.
6. Real run: `full_reload = True, allow_full_scan = True, max_parallel = 12, max_retries = 1, table_filter = ""`. Expect `SUCCESS` and an unchanged watermark row.
7. Repeat step 6 to prove idempotency: inserted 0 on every table, identical row counts, identical non-technical column values.
8. Normal incremental run (`full_reload = False`). Expect `SUCCESS` or `NO_DATA`. Every table shows `stale_rows` equal to `input_rows` for the 33 documents if they are re-read. The watermark is not lower than the snapshot of 10.1.
9. Verify that the 5 deactivated tables and `slv_3p_poi_policy` have the same Delta version as in 10.1. Verify that the frozen columns are unchanged for rows not touched by the rerun.

Promotion to STG/PROD repeats 10.1–10.2 per environment.

### 10.3 Data effects of the rerun

Only the `poi_id`s present in current bronze are rewritten, in the 8 active tables. `slv_3p_poi_opening_hours` gains the physical `open_now` column; historical rows get NULL there. Rows from the old enriched load stay as they are (INV-8).

### 10.4 Rollback

1. Pause 3P runs (confirm the lock is free).
2. Revert the three notebooks and the docs in Git (user action) and redeploy the old extract notebook.
3. Restore config with targeted writes, not table-wide `RESTORE`, because the control tables are shared with partner. Run the old `NB_CREATE_DDL` 3P registry seed cell (`replaceWhere` on the 3P source), then `UPDATE ctrl_mng_pipeline_config SET is_active = 1` for the 5 tables with the same scope predicate as the deactivation cell.
4. Silver: no rollback is needed for correctness. The old notebook ignores `open_now`, and the old columns are still physically present. The old notebook's next `full_reload` repopulates old-config columns for current bronze. Enrichment, review_i18n, content, price, and raw_data stay `NO_DATA` because bronze has no such blocks. As a last resort, `RESTORE TABLE <slv_3p_poi_x> TO VERSION AS OF <10.1 version>` applies per 3P-only table. Restoring `slv_3p_poi_opening_hours` also removes `open_now` from its schema.
5. `ctrl_cdc_state`: no action. The rerun wrote equal-order rows.
6. Watermark: no action. `full_reload` did not move it.

### 10.5 Forward recovery

| Situation | Action |
|---|---|
| `CastNullError` on `open_now` or another column | Record the run, add a probe for the offending type (counts only), then either fix the registry type through a decision or rerun once with `cast_null_policy = WARN` after the user accepts the risk |
| Table FAILED during rollout | `full_reload = True, table_filter = <failed tables>` |
| `watch.inactive_blocks` or `watch.extra_info_nonempty` > 0 | Do not reactivate silently. Open a new task: probe the block shape, then re-add registry rows (`DOC` / `DOC_ARRAY` only) or design L2 handling |
| `watch.unknown_top_keys` non-empty | Registry change through a new task (add a column via an INSERT into the registry, then a `full_reload` of that table) |
| Lost lock / stale lock | Lib procedures in `CTRL_TABLES_CONTEXT.md` §4 |

## 11. L2 contract

### 11.1 General

- No L2 node and no `RECOMPUTE` edge may read `slv_3p_poi_enrichment`, `slv_3p_poi_review_i18n`, `slv_3p_poi_content`, `slv_3p_poi_price`, `slv_3p_poi_raw_data`, or `slv_3p_poi_policy`.
- No L2 node may read `slv_3p_poi.available_langs_json`, `slv_3p_poi.enrichment_failed_langs_json`, or any of the 38 amenity flag columns of `slv_3p_poi_amenity`.
- RECOMPUTE edges are currently not seeded in `lh_vv_ctrl` (`NB_00_ORCHES_SLV_TO_GLD.md` §1), so nothing reads the deactivated tables today. The future edge seed must contain no edge whose `src_tbl` is a deactivated table.
- Child-element disappearance is detected in L2 with `_last_seen_at` against `slv_3p_poi._last_seen_at` of the same `poi_id` (INV-7).

### 11.2 N2 `slv_poi` input contract

Inputs: N1 `slv_poi_source_map`, `slv_3p_poi`, `slv_pn_business_services`, `slv_pn_partners`, `ref_business_category`, `ref_source`. `slv_3p_poi_enrichment` is removed.

| N2 output (3P rows) | Source |
|---|---|
| `business_sector`, `business_category`, `poi_type` | `ref_business_category` keyed by (`source_name`, `slv_3p_poi.business_sector`, `slv_3p_poi.business_category`); no enrichment fallback |
| `subcategory_tags` | `slv_3p_poi.subcategory_tags_json` |
| types, where N2 consumes them | `slv_3p_poi.types_json` |
| `operating_status` | `slv_3p_poi.operating_status` |
| `brand_name` | NULL (no brand field in the raw payload) |
| `model_business_sector`, `model_type` | NULL (no model field) |

Partner rows are unchanged.

### 11.3 N4 `slv_poi_localization` input contract

Inputs: N1, `slv_3p_poi`, `slv_pn_business_services`, `slv_pn_business_service_i18ns`, `ref_lang_policy`, `ref_source`. `slv_3p_poi_enrichment` and `slv_3p_poi_content` are removed.

- Real name: one (`poi_id`, `lang = slv_3p_poi.language_code`) row with name = `slv_3p_poi.poi_name`. Choosing `poi_name_normalized` instead is not part of this contract.
- Other languages: name only, via `ref_lang_policy` `FALLBACK_UNACCENT` / `FALLBACK_COPY`. These remain L2 rules.
- Description: NULL for every 3P language row. Never copied from another language.
- Slug, `has_required_langs`, `legacy_poi_id`: unchanged rules. Slug is issued once, so existing slugs are kept.

### 11.4 N1, N3, N5

No input change. N1 reads `slv_3p_poi` identity and seen columns only. N3 reads `slv_3p_poi_address`, unchanged. N5 reads N3.

### 11.5 Implementation gate for N2/N4

Implementation waits until the `NB_SLV_POI` and `NB_SLV_POI_LOCALIZATION` notebooks are in the repository. That later change must, before coding:

- grep the node SQL for the forbidden tables and columns of §11.1;
- run a counts-only probe of `slv_3p_poi.language_code` distribution and of `ref_business_category` coverage of the current (`source_name`, `business_sector`, `business_category`) pairs. The outcome of `has_required_langs` and of the sector mapping depends on these counts;
- preview the gold diff (`gld_srv_poi_multi_lang.short_description` becomes NULL for 3P), because it drives PostgreSQL sync volume.

The current L1 change does not depend on these facts.

## 12. Observability

- Exit JSON / `RUN_SUMMARY`: `docs_by_table` (8 keys), `bad_shape`, `watch` (new), plus lib summary fields.
- `ctrl_log_run`: `run_mode` (`FULL_RELOAD` for the rerun), `read_mode`, read / valid / ignored / rejected counts, `watermark_to`, `run_params` without lang keys.
- `ctrl_log_table_run`: 8 rows per run, with `input_rows`, `stale_rows`, `applicable_rows`, `entity_rows`, `inserted_rows`, `updated_rows`, `cast_null_rows`, `rejected_rows`.
- WARN log lines: watch counters, `bad_shape`, cast-null under WARN.
- Runbook queries: the existing three in the notebook's "Vận hành" cell, plus "watermark row unchanged after `full_reload`" and "frozen tables' Delta version unchanged".

## 13. Security and data handling

- The drift counters expose top-level key names and counts only, never values. Key names come from the payload schema, not from user content.
- `ctrl_cdc_reject.after_payload` keeps the existing behavior: payload of rejected documents, stored in `lh_vv_ctrl`. Unchanged.
- The review and media tables keep the existing personal-data exposure (author names, photographer). No new personal field is added. `open_now` is not personal data.
- Task artifacts, probes, and results must stay counts-only. No payload values, URLs, phone numbers, review text, or names.
- No secrets, no new connections, no gold read.

## 14. Implementation plan for Main

Execute in this order. Run `python scripts/vv.py verify 20261009-redesign-3p-silver-raw-payload` after step 5.

1. `notebooks/NB_CREATE_DDL.ipynb`
   - `TABLE_CONFIGS_3P` cell:
     - Add a `[SỬA 09/10]` header block that cites E1 and the user decision.
     - Delete `AMENITY_FLAGS` and `AMENITY_FLAGS_OFF`.
     - `slv_3p_poi`: remove `available_langs_json` and `enrichment_failed_langs_json` with `[BỎ 09/10]` comments.
     - `slv_3p_poi_opening_hours`: append `"open_now": _bool("open_now")` and delete the D3 comment.
     - `slv_3p_poi_amenity`: keep three columns and rewrite the `ext_attributes_json` comment to the new payload (string values; union of keys; no 62-key claim).
     - Delete the `slv_3p_poi_price`, `slv_3p_poi_raw_data`, `slv_3p_poi_content`, `slv_3p_poi_enrichment`, and `slv_3p_poi_review_i18n` entries, leaving one `[BỎ 09/10]` comment that lists them.
     - In the `json_path` legend, mark `_lang`, `_langs`, and `_align` as unused by 3P.
   - Seed cell comment: 9 tables, 93 columns (15 inactive); keys `poi_id`, `review_id` (`HASH_SHA256`), `media_dedup_key` (`HASH_SHA256_PIPE`).
   - 3P `ctrl_mng_pipeline_config` INSERT: set `is_active` to 0 for seq 4, 9, 10, 13, 14.
   - New `%%sql` cell right after that INSERT: `UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0 WHERE pl_name = 'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00' AND src_schema = 'lh_vv_bronze.dbo' AND src_tbl = 'brz_3rd_crawler_poi_stream' AND trg_schema = 'lh_vv_silver.dbo' AND trg_tbl IN ('slv_3p_poi_price','slv_3p_poi_raw_data','slv_3p_poi_content','slv_3p_poi_enrichment','slv_3p_poi_review_i18n') AND is_active <> 0;` followed by a `SELECT trg_tbl, load_mode, is_active` over the 3P rows. Add a Vietnamese comment: tắt, không xoá; rollback = `SET is_active = 1`.
2. `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`: §9 items 1–12.
3. `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`:
   - Update §1 (8 active tables, DOC / DOC_ARRAY only), §3 (remove LANG rows), §4 (remove the four parameters), §5 (constants), §6 (flow without langs, with watch), and §7 (functions).
   - Update §8 to show 8 active tables plus the frozen list and the JSON columns without `available_langs_json` / `enrichment_failed_langs_json`.
   - Update §10 (rollout with `full_reload`; replace "Thêm ngôn ngữ") and §11 (remove M7 LANG_ARRAY; add the frozen-columns note).
4. `docs/context/01_DATA_MODEL.md`:
   - §5.2: 14 tables with 8 active, 93 registry columns (78 active), the column table, and the frozen tables and columns.
   - §6: N2 and N4 inputs per §11.2 / §11.3, and a note that implementation is pending the node notebooks.
   - §3 diagram label `slv_3p_poi_*`.
5. `docs/context/CTRL_TABLES_CONTEXT.md`:
   - §3: 3P pipeline-config table with the `is_active` values, and a note that 3P accepts DOC / DOC_ARRAY only.
   - §5: 3P registry totals and table list.
   - Add a 09/10 change-log row.
6. `tests/test_3p_l1_contract.py`: pure Python, no Spark, ruff-clean.
   - Load `NB_CREATE_DDL.ipynb` as JSON, find the cell that defines `TABLE_CONFIGS_3P`, and `exec` it in an empty namespace. The cell has no Spark dependency. Then assert:
     - 9 tables and 93 columns, 15 with `active` False;
     - the active table set of §4.2 and the per-table counts;
     - the three key formulas (INV-3);
     - `open_now` is boolean on the opening-hours table;
     - amenity has exactly 3 columns;
     - no path part has a head in `_lang`, `_langs`, `_align`, `extra_info`;
     - every non-technical top-level path head is in the §1.2 top-level key set.
   - Load the extract notebook JSON and assert:
     - the parameters cell defines none of `langs`, `lang_object_path`, `lang_map_path`, `lang_field`;
     - the source defines `EXTRACT_MODES = ("DOC", "DOC_ARRAY")`;
     - the source contains no `lang_entries`, `LANG_MODES`, or `_lang_entries`.
   - Assert that the deactivation cell's `IN (...)` list equals the 5 table names.
7. Main writes `runtime-runbook.md` in Vietnamese covering §10.1–§10.5 and §15.2, and records any deviation from this document in `decision.md` before coding.

## 15. Verification strategy

### 15.1 Local (deterministic)

`python scripts/vv.py verify 20261009-redesign-3p-silver-raw-payload` must pass: ruff on the new test, pytest including `tests/test_3p_l1_contract.py`, and task-state validation. `.ipynb` files are not covered by `cmd_verify` JSON checks, so the test parses both notebooks with `json.loads`. That also proves the notebooks are valid JSON.

### 15.2 Runtime (Fabric DEV, user runs the runbook)

| Check | Pass criterion |
|---|---|
| Config | 8 active and 6 inactive 3P pipeline rows; registry 9 tables / 93 columns / 15 inactive |
| Dry run | no `ConfigError`; 8 table results; `cast_null` empty; `watch` all zero |
| `full_reload` | `SUCCESS`; 8 tables SUCCESS or NO_DATA; `open_now` non-null count reported (counts only); watermark row byte-identical to 10.1 |
| Rerun `full_reload` | inserted 0 on all tables; row counts and non-technical columns equal to the previous run |
| Incremental | `SUCCESS` / `NO_DATA`; `last_src_version` ≥ 10.1 value; no backward move |
| State / reject | 3P state rows only for the 8 active tables were updated in these runs; no new reject rows unless bronze holds invalid documents (counts by reason) |
| Frozen tables | Delta version of the 5 deactivated tables and policy unchanged |
| Concurrency | starting a second non-dry 3P run while one holds the lock yields `SKIPPED_CONCURRENT` |

### 15.3 Review routing

`sql-data-reviewer` (registry, MERGE unchanged, deactivation SQL), `spark-runtime-reviewer` (notebook edits, drift counters, cache), `state-correctness-reviewer` (`full_reload` vs state and watermark, frozen columns, config-change window), and `fabric-pipeline-reviewer` (exit JSON `langs` → `watch`, no FL_00 change). `risk-gate` is required by the high risk level.

## 16. Evidence needed

None for this architecture. Every L1 decision rests on E1 / E1b population counts for the current bronze table and on the user decisions of 2026-10-09.

Runtime facts that this design checks instead of assuming:

- the `open_now` value type across documents, caught by `cast_null_policy = FAIL` in the dry run;
- future reappearance of enrichment or null blocks, caught by the `watch` counters.

The N2/N4 implementation gate of §11.5 carries its own probes and is out of scope for this task.
