RESULT: PASS

## Main brief

### Decision
PASS. The revised `model-design.md` meets all four previous PASS criteria: no CMS column uses `DATE_DAYS` (`first_publish_date` is `date`/`NONE`), Conflicts 3–5 are answered, grain and keys are unchanged, and a blank `locale` stays `''`. B1 and B2 are closed.
Build a new per-source notebook from the 3P structure with no lib diff. It routes by `source_name` through `TABLE_SOURCE`, uses `state_key=row`, null-safe key matching, and a MERGE guard ordered by `cms_updated_at` first. Seed 4 DOC config rows, 48 registry rows, and 1 watermark row in both DDL notebooks.
B3 (14 non-matching blog time values) gates the first real run, not implementation.

### Invariants Main must preserve
- I-1 Each `slv_cms_*` table receives only events with `lower(trim(source_name)) == TABLE_SOURCE[trg_tbl]`. `presence` has no `F.lit(True)` branch.
- I-2 The MERGE `ON` uses `<=>` for every column in `spec.key_cols` (`document_id`, `locale`). Column names are not hard-coded.
- I-3 Bronze `type` and `ingested_date` are never read. There is no `RAW_LANG`, lang parameter, or `_langs` path.
- I-4 `state_key` is `row`. Any other value raises `ConfigError` in `build_context`.
- I-5 Blank `source_name` → `MISSING_ENTITY_KEY`. Blank, open, corrupt, or non-object payload → `INVALID_PAYLOAD`. NULL `crawled_at` → `MISSING_EVENT_ORDER`. All go to `ctrl_cdc_reject` with `src_tbl=cms_raw_data`.
- I-6 Element null/blank checks cover `document_id` only. A null `locale` is loaded as NULL and a blank one as `''`. Neither is rejected or defaulted.
- I-7 The guard orders by `coalesce(cms_updated_at)`, then `_crawled_at`, then `_event_id` (`>=`). `resolve_latest` puts `cms_updated_at desc_nulls_last` first.
- I-8 The watermark advances only when every table ends SUCCESS or NO_DATA. Never on `dry_run`, `full_reload`, or `table_filter`.
- I-11 No CMS registry row has `DATE_DAYS`, and `locale` has no rule.
- No diff to `NB_LIB_EXTRACT_RAWDATA`, the 3P extract, or the partner extract. No pipeline activity. Logs and docs carry no payload text or URLs.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| E1 | `notebooks/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb` (new) | parameters/constants cell | `RAW_PAYLOAD="raw_payload"`, `RAW_EVENT_ID="event_id"`, `RAW_DOC_ID=("source_name",)`, `TABLE_SOURCE` (4 entries), `NULLABLE_KEYS=("locale",)`, `doc_key_column="document_id"`, `state_key="row"`, default `sources` = 4 values, `cast_null_policy="FAIL"`; lang constants removed | `test_table_source_covers_all_four_tables`, `test_state_key_is_row_and_doc_key_is_document_id`, `test_no_type_or_lang_column_read` pass |
| E2 | same | `read_raw`, `classify_docs`, `presence`, `profile_docs` | A2 routing, A3 classification order | `test_presence_routes_by_source_name` passes |
| E3 | same | `build_table_rows`, `element_reject_rows` | `needed=[document_id]`; key = `concat_ws("|", document_id, locale)`; `_parse_failed` still rejects | `test_key_null_checks_document_id_only` passes |
| E4 | same | `resolve_latest`, `build_merge_sql` | A5 order; guard per full doc `#### Guard and ON clause` | `test_merge_on_is_null_safe`, `test_merge_guard_orders_by_cms_updated_at_first`, `test_resolve_latest_orders_by_cms_updated_at_first` pass |
| E5 | same | `reject_frame`, `doc_source_payload`, `doc_reject_rows` | A3 reject identity (`src_db=source_name`, `entity_key=source_name|event_id`, `event_hash` over event_id, source_name, crawled_at, payload) | reject columns match 3P shape |
| E6 | same | `build_context`, `check_config` | `ConfigError` if a `trg_tbl` is unmapped, a source is not in `sources`, a spec is not DOC with `$`, `state_key != row`, or `cms_updated_at` is not active | `test_cms_updated_at_active_on_all_tables` passes |
| E7 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | new cell `init_cfg_cms` after `init_cfg_3p`; `init_plan` (`third_rows` line); `init_seed_ctrl` | `TABLE_CONFIGS_CMS` per full doc `### A8. Seed config shape`; flatten + `validate_rows` + `registry_rows += cms_rows`; 4 tuples `(_FL00,_B,'cms_raw_data',_S,'slv_cms_*',1,1,'DOC',None,None,None)`; watermark `wm_transform_cms_raw_data` on `crawled_at` | `test_cms_seed_rows_present`, `test_no_date_days_on_cms_registry`, `test_no_rule_on_locale`, `test_first_publish_date_is_date_none`, `test_registry_columns_match_model_design` pass |
| E8 | `notebooks/NB_CREATE_DDL.ipynb` | new markdown + code cells at the end, `[THÊM 08/11] 20261104-extract-cms-raw-data` | Same config, registry, and watermark rows, insert if absent; `seed_registry(TABLE_CONFIGS_CMS, "lh_vv_bronze.dbo", "cms_raw_data")` | `test_seed_cells_match_between_ddl_notebooks` passes; rerun is a no-op |
| E9 | `tests/test_cms_l1_contract.py` (new) | — | static-parse tests listed below | all pass |
| E10 | `tests/test_initial_ddl_contract.py` | seed assertions | add `test_cms_seed_rows_present` | passes |
| E11 | `docs/context/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.md` (new) | 3P context-doc section pattern | flow, routing, A5 guard, A6 null locale, A7 dry-run gate, operator reject query | doc exists; no URLs or payload text |
| E12 | `docs/context/CTRL_TABLES_CONTEXT.md` | `### Dữ liệu hiện có` in §3, §4, §5; §10 | CMS config, watermark, and registry summary; history row | rows listed |

### Order and stop points
1. E7, then E8 (seeds; the A8 shape is shared). E10 tests.
2. E1–E6 (notebook), then E9 tests.
3. E11, E12 docs.
4. Run the local verification. STOP (evidence) if any test fails or the lib/3P/partner diff is not empty.
5. Optional DEV rollout (runtime not required): run the patch cell, then a dry run with `allow_full_scan=True`. STOP (evidence): if `slv_cms_blog` has `cast_null > 0`, run probe P4 (full doc `## Required probes and decisions`) and save `evidence/results/cms-blog-time-nonmatch.md`. STOP (user decision U6) before the first real run.
6. No pipeline activity or schedule. STOP (user decision) before any scheduling.

### Tests and verification
- `python -m pytest tests/test_cms_l1_contract.py tests/test_initial_ddl_contract.py tests/test_3p_l1_contract.py -q`
- `git diff --exit-code notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`
- `tests/test_cms_l1_contract.py`: `test_table_source_covers_all_four_tables`, `test_presence_routes_by_source_name`, `test_state_key_is_row_and_doc_key_is_document_id`, `test_no_type_or_lang_column_read`, `test_key_null_checks_document_id_only`, `test_merge_on_is_null_safe`, `test_merge_guard_orders_by_cms_updated_at_first`, `test_resolve_latest_orders_by_cms_updated_at_first`, `test_registry_keys_document_id_locale`, `test_cms_updated_at_active_on_all_tables`, `test_no_date_days_on_cms_registry`, `test_no_rule_on_locale`, `test_first_publish_date_is_date_none`, `test_registry_columns_match_model_design` (48 rows, in model `column_order`), `test_config_rows_doc_mode_fl00`, `test_watermark_row_seeded`, `test_seed_cells_match_between_ddl_notebooks`.
- `tests/test_initial_ddl_contract.py`: `test_cms_seed_rows_present`.

### Read only if needed
- `## Verdict` → why this is PASS; lib facts for `NONE`, `ISO_UTC_TS`, `resolve_type`.
- `### A1. New notebook from the 3P structure` → E1.
- `### A2. Source routing` → E2, E6.
- `### A3. Classification and reject identity` → E2, E5.
- `### A4. State granularity` → E1, E6.
- `### A5. Ordering: cms_updated_at first` → E4, E6.
- `### A6. Null locale in the key`, `#### Guard and ON clause` → E3, E4.
- `### A7. B3 as a rollout gate`, `## Rollout` → stop point 5, E11.
- `### A8. Seed config shape` → E7, E8.
- `## Transaction and commit boundaries`, `## Idempotency` → E7, E8 (insert if absent), E4.
- `## Observability` → E1 (`extra.null_locale_rows`), E11.
- `## Required probes and decisions` → P4 spec, U6.

# Architecture: 20261104-extract-cms-raw-data (D-19 round)

## Verdict

D-18 and D-19 approved this round after the D-16 round returned `EVIDENCE_REQUIRED`. The model has been revised under D-17 (U5). It meets all four items of the previous `### PASS criteria for the next round`:

| # | Criterion | Revised `model-design.md` | Met |
|---|---|---|---|
| 1 | No CMS registry row uses `DATE_DAYS`; `first_publish_date` is `date`/`NONE` or `string` | `### slv_cms_blog`: `first_publish_date` `date`, `convert_rule = NONE`. `## Columns` intro: "No CMS registry row uses `DATE_DAYS`" | yes |
| 2 | Conflicts 3, 4, 5 answered and `## Columns` matches | `## Conflicts and questions` items 3, 4, 5 are marked Answered (D-17). The blog and news "not modelled" notes and the `*_json` names match | yes |
| 3 | Grain, keys, `src_object = $`, `DOC`, `cms_updated_at` unchanged | `## Entities and grain`, `## Keys`, `### Columns shared by all four tables` | yes |
| 4 | Blank `locale` kept as `''` | `## Keys` last bullet, `locale` row: "A blank value stays `''`" | yes |

The model changed nothing else that affects the flow design. Items 1, 2, and 7 are closed by A5 and A6. Item 6 is a follow-up task. The flow design from the D-16 round stands, with B1 and B2 closed. B3 remains a rollout gate only (A7).

Code checked this round:
- Lib `CONVERT_RULES["NONE"] = "{cast}({col} AS {dt})"`. `CAST_FN` is `TRY_CAST` under ANSI and `CAST` otherwise. A malformed `first_publish_date` string therefore becomes NULL and is counted as a cast-null. It does not raise. This is covered by the A7 gate.
- Lib `validate`: a `TIME_RULES` rule (which includes `ISO_UTC_TS`) is valid only on `timestamp`, and `DATE_DAYS` only on `date`. The model's `cms_*_at` and promotion datetimes are `timestamp` with `ISO_UTC_TS`, so they pass.
- Seed `resolve_type("date")` returns `("date", "NONE")`. A column given only `"type": "date"` therefore seeds `NONE`. `flatten_table_configs` accepts `"key"` as a list and sets `key_order` from list order.
- `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` still defines all 13 functions this design adapts.

| # | Gap | Status |
|---|---|---|
| B1 | `first_publish_date` was `DATE_DAYS` | Closed (D-17, model revision) |
| B2 | Conflicts 3, 4, 5 | Closed (D-17) |
| B2' | `slv_cms_` prefix missing from naming docs | Follow-up task; `02_NAMING_CONVENTION.md` is not in `scope.files` |
| B3 | 14 non-matching closed blog time values (D-12) | Rollout gate (A7, P4, U6) |

## Scope

- New `notebooks/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb` (D-15 U2), built from the 3P notebook structure. It calls `load_table_specs(ctx, SNAPSHOT_MODES)` (D-02).
- Ctrl seeds in `NB_SETUP_INITIAL_DDL` (fresh environment) and `NB_CREATE_DDL` (patch cell, insert if absent): 4 `ctrl_mng_pipeline_config` rows, the registry rows from `model-design.md` `## Columns`, and 1 watermark row.
- The four `slv_cms_*` tables are created by lib `ensure_target`/`target_ddl` from the registry. No DDL is written by hand.
- Offline contract tests, a new context doc, and updates to `CTRL_TABLES_CONTEXT.md`.

## Non-goals

- No new `LOAD_MODES` value and no lib diff (D-01, D-02). The 3P and partner notebooks have no diff.
- No pipeline activity, FL_00 included (D-03), and no schedule.
- No `DOC_ARRAY`, no `pois[]` or `formats.*` path (D-04), no gold (D-10), no `poi_id`.
- No repair or defaulting of payloads or `locale` (D-15 U1, U4).
- No edit to `02_NAMING_CONVENTION.md` (follow-up task).
- Blog `author`, `cover_image`, `destination`, `gallery`, and news `cover_image` are not modelled (D-17).

## Invariants

- I-1 Each `slv_cms_*` table receives only events where `lower(trim(source_name)) == TABLE_SOURCE[trg_tbl]`. No event reaches two tables.
- I-2 One row per (`document_id`, `locale`). `locale` may be NULL. The MERGE `ON` clause uses `<=>` for every key column.
- I-3 Bronze `type` and `ingested_date` are never selected. `locale` comes only from `json_path = locale`. There is no `RAW_LANG`, no lang parameter, and no `_langs` path.
- I-4 `state_key = row`. An event for one locale never makes another locale's event stale.
- I-5 A blank `source_name`, a blank, open, corrupt, or non-object payload, or a `crawled_at` that casts to NULL goes to `ctrl_cdc_reject` (`src_tbl = cms_raw_data`) and reaches no silver table.
- I-6 An element whose `document_id` is null or blank goes to element reject. A null `locale` is loaded as NULL and is never rejected or defaulted. A blank `locale` stays `''`.
- I-7 A target row changes only when the source wins the CMS guard (A5). A replay changes no business column.
- I-8 The watermark advances only when every processed table ends SUCCESS or NO_DATA. `table_filter`, `full_reload`, and `dry_run` never advance it.
- I-9 Ctrl state and reject MERGEs touch only `src_tbl = cms_raw_data`.
- I-10 Logs, exit JSON, and task artifacts carry no payload text, URLs, or signatures. Payload copies in reject rows and in JSON-text columns are accepted (D-15 U3).
- I-11 No CMS registry row uses `DATE_DAYS`, and no CMS registry row has a rule on `locale`.

## State ownership

| State | Owner | Writer | Readers |
|---|---|---|---|
| `slv_cms_*` rows | this notebook | one worker per table (`run_merge`) | later silver L2 (out of scope) |
| watermark `wm_transform_cms_raw_data` (`src_tbl = cms_raw_data`, `trg_tbl` NULL, `watermark_column = crawled_at`) | this notebook | main thread: lock, finalize | this notebook |
| `ctrl_cdc_state`, partition `cms_raw_data` | this notebook | main thread `commit_state` | `load_state` |
| `ctrl_cdc_reject`, partition `cms_raw_data` | this notebook | main thread `merge_rejects` | operators |
| `ctrl_log_run`, `ctrl_log_table_run` | lib | main thread | operators |
| config and registry rows with `src_tbl = cms_raw_data` | seed notebooks | `NB_SETUP_INITIAL_DDL`, `NB_CREATE_DDL` | this notebook (read only) |
| `TABLE_SOURCE` map | notebook constant | code review | this notebook |

## Grain and keys

See `model-design.md` `## Entities and grain` and `## Keys`: DOC `$`, `document_id` (key_order 1), `locale` (key_order 2). This design adds no key. `doc_key_column = document_id` exists only to satisfy `check_config`. Because `state_key = row`, it does not set state identity.

## Architecture decisions

### A1. New notebook from the 3P structure

| Option | Result |
|---|---|
| Parameterize the 3P notebook | Touches a running flow and needs routing and lang changes inside it. Rejected. |
| Generic lib entry point | Lib change, ruled out by D-02. Rejected. |
| **New per-source notebook copied from 3P** | Duplicates notebook code, but isolates the CMS flow. **Selected.** |

Constants: `RAW_PAYLOAD = "raw_payload"`, `RAW_EVENT_ID = "event_id"`, `RAW_DOC_ID = ("source_name",)`. Remove `RAW_LANG`, `lang_object_path`, `lang_map_path`, and `lang_field`. Read `raw_payload`, `event_id`, `source_name`, and `crawled_at`, plus `_doc.*` from the registry.

### A2. Source routing

`TABLE_SOURCE = {"slv_cms_blog": "strapi_blog", "slv_cms_destination": "strapi_destination", "slv_cms_news": "strapi_news", "slv_cms_promotion_article": "strapi_ph_promotion_article"}`.
- `presence(spec)` = `lower(trim(_doc__source_name)) == TABLE_SOURCE[spec.trg_tbl]`. It has no `F.lit(True)` branch.
- `check_config` raises `ConfigError` when an active `trg_tbl` is missing from `TABLE_SOURCE`, a mapped source is missing from `sources`, or a spec is not DOC with `$`.
- `sources` defaults to the four values. Any other value becomes IGNORED `OUT_OF_SCOPE`.
- Rejected alternatives: a new config column (a ctrl schema change), reusing `src_object_schema` (forbidden for snapshot modes), and a `json_path` filter (not supported by the lib).
- FL_00 pre-check: the CMS rows carry `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` (D-15 U2). The pre-check filters on `pl_name` and `src_tbl = 'partner_raw_data'` (`CTRL_TABLES_CONTEXT.md` §2), so the CMS rows do not affect it, the same as the existing 3P rows. NB_00 reads only `RECOMPUTE` rows.

### A3. Classification and reject identity

The 3P rules apply in this order:
1. A blank `source_name` → REJECTED `MISSING_ENTITY_KEY`.
2. A source outside `sources` → IGNORED `OUT_OF_SCOPE`.
3. A blank, corrupt, open, or non-object payload → REJECTED `INVALID_PAYLOAD` (D-15 U1).
4. A `crawled_at` that casts to NULL → REJECTED `MISSING_EVENT_ORDER` (0 rows per D-12).

A document reject row has `src_db = source_name`, `cdc_op` NULL, `before_payload` NULL, `after_payload` = the payload, and `source_payload = {event_id, source_name, crawled_at}`. Its `entity_key` is `source_name|event_id`, and its `event_hash` is `sha256(event_id, source_name, crawled_at, payload)`. The element reject `ident` drops `_lang` and `_align`.

### A4. State granularity

`state_key` is fixed to `row`, and `build_context` raises `ConfigError` for any other value. With `doc`, state would key on `document_id` across locales, which breaks I-4.

### A5. Ordering: `cms_updated_at` first

D-14 found no `crawled_at` ties, but `updatedAt` order differs from crawl order on 146, 99, 12, and 27 keys.

| Option | Result |
|---|---|
| Lib order only (`_crawled_at`, `_event_id`) | Silver can keep an older CMS version for up to 284 keys. This contradicts the `updatedAt` guard in the business reference (D-10). |
| **`cms_updated_at` first, then `_crawled_at`, `_event_id`** | Silver keeps the newest CMS version. Only notebook-owned functions change. **Selected.** |
| `updatedAt` in state as well | Needs a change to lib `event_order` and the state struct. Rejected (D-02). |

- `resolve_latest`: put `F.col("cms_updated_at").desc_nulls_last()` before the existing order list.
- `build_merge_sql`: use the CMS guard (`#### Guard and ON clause`). Everything else follows 3P: tech columns, `created_at` on INSERT only, `updated_at` from the merge clock, and no DELETE.
- State `_is_stale` stays on the lib crawl order. Accepted edge case: across runs, a late event with an older `crawled_at` but a newer `updatedAt` is skipped as stale. Within one run, `resolve_latest` handles it.
- `_last_seen_at` moves only when the guard passes.
- `cms_updated_at` must be an active registry column on all four tables. If it is not, `check_config` raises `ConfigError`.

### A6. Null `locale` in the key

- `build_table_rows` and `element_reject_rows`: `needed = [document_id]`. `NULLABLE_KEYS = ("locale",)` is excluded from the null/blank check. `_parse_failed` still rejects.
- `row_key`/`_entity_key` = `concat_ws("|", document_id, locale)`. A NULL `locale` gives `doc`, a blank one gives `doc|`, and a value gives `doc|vi`. These keys are distinct because `document_id` contains no `|` (a contract test pins this).
- `Window.partitionBy(document_id, locale)` groups NULL locales together.
- `target_ddl` emits no `NOT NULL`.

#### Guard and ON clause

```
ON  t.`document_id` <=> s.`document_id` AND t.`locale` <=> s.`locale`
WHEN MATCHED AND (
      coalesce(s.`cms_updated_at`, TIMESTAMP'0001-01-01 00:00:00')
    > coalesce(t.`cms_updated_at`, TIMESTAMP'0001-01-01 00:00:00')
  OR (     coalesce(s.`cms_updated_at`, TIMESTAMP'0001-01-01 00:00:00')
         = coalesce(t.`cms_updated_at`, TIMESTAMP'0001-01-01 00:00:00')
       AND (s.`_crawled_at` > t.`_crawled_at`
            OR (s.`_crawled_at` = t.`_crawled_at` AND s.`_event_id` >= t.`_event_id`)))
) THEN UPDATE SET <3P update list>
WHEN NOT MATCHED THEN INSERT <3P insert list>
```

Build `ON` from `spec.key_cols` with `<=>`. Do not hard-code the column names.

### A7. B3 as a rollout gate

| Option | Result |
|---|---|
| P4 blocks implementation | A probe about 14 values out of 79766 would hold up all code. |
| **P4 gates the first real run** | No code depends on the outcome. U6(a) and U6(b) change only the run parameter `cast_null_policy`. U6(c) is a registry fix plus `full_reload`. The dry run shows `cast_null` by column before any real write. **Selected.** |

`first_publish_date` with `NONE` turns a blank or malformed string into NULL through `CAST`/`TRY_CAST`. This is counted as a cast-null, so the gate also covers it.

### A8. Seed config shape

The seed uses the existing `TABLE_CONFIGS` dict format with `"key": ["document_id", "locale"]` (list order sets `key_order`). Column names, paths, and types come from `model-design.md` `## Columns`, in its `column_order`. The registry adds no other columns. Shape:

```python
# [THÊM 08/11] 20261104-extract-cms-raw-data
def _cms_ts(path):
    return {"path": path, "type": "timestamp", "rule": "ISO_UTC_TS"}

_CMS_COMMON = {
    "document_id": _str("documentId"),
    "locale": _str("locale"),            # no rule (D-17)
    "id": {"path": "id", "type": "bigint"},
    "slug": _str("slug"),
    "cms_created_at": _cms_ts("createdAt"),
    "cms_updated_at": _cms_ts("updatedAt"),
    "cms_published_at": _cms_ts("publishedAt"),
}

def _cms(table, extra):
    return {"source_table": "$", "target_schema": _S, "target_table": table,
            "key": ["document_id", "locale"], "columns": {**_CMS_COMMON, **extra}}

TABLE_CONFIGS_CMS = [
    _cms("slv_cms_blog", {
        "title": _str("title"), "sapo": _str("sapo"),
        "first_publish_date": {"path": "first_publish_date", "type": "date"},  # NONE
        "block_content_json": _str("block_content"), "seo_json": _str("SEO"),
        "platforms_json": _str("platforms"), "pois_json": _str("pois")}),
    _cms("slv_cms_destination", {
        "name": _str("name"), "description": _str("description"),
        "cover_gallery_json": _str("cover_gallery"), "seo_json": _str("SEO"),
        "faq_json": _str("FAQ"), "experiences_json": _str("experiences"),
        "highlight_json": _str("highlight"), "pois_json": _str("pois")}),
    _cms("slv_cms_news", {
        "title": _str("title"), "sapo": _str("sapo"), "is_featured": _bool("is_featured"),
        "block_content_json": _str("block_content"), "seo_json": _str("SEO"),
        "news_category_json": _str("news_category")}),
    _cms("slv_cms_promotion_article", {
        "title": _str("title"), "short_description": _str("shortDescription"),
        "voucher_code": _str("voucherCode"),
        "promotion_start_datetime": _cms_ts("promotionStartDateTime"),
        "promotion_end_datetime": _cms_ts("promotionEndDateTime"),
        "usage_start_datetime": _cms_ts("usageStartDateTime"),
        "usage_end_datetime": _cms_ts("usageEndDateTime"),
        "content_json": _str("content"), "terms_json": _str("termsAndConditions"),
        "pois_json": _str("pois")}),
]
```

`_str`, `_bool`, and `_S` come from `init_cfg_3p` in `NB_SETUP_INITIAL_DDL` and from the 3P seed cell in `NB_CREATE_DDL`. The `NB_CREATE_DDL` patch cell must define them locally or reuse the ones already in scope, and must not redefine `POI_ID`. Pipeline rows: `(_FL00, _B, 'cms_raw_data', _S, '<slv_cms_*>', 1, 1, 'DOC', None, None, None)` × 4.

## Ordering

Within one run:
1. Lock.
2. Write the run log as RUNNING.
3. Pin the bronze version and read the range.
4. Classify, then profile (`docs_by_table` through `presence`).
5. `load_state`.
6. Process the 4 tables in one wave.
7. `decide_status`.
8. Commit: state, then rejects, then the table log.
9. Finalize the watermark.
10. Close the run log and unlock.

Version ranges are contiguous across runs. The tables do not depend on each other.

## Transaction and commit boundaries

| Step | Commits | On failure |
|---|---|---|
| Target MERGE | 1 per table | The table is FAILED and nothing is staged for it. The other tables continue. |
| `commit_state` | 1 MERGE (SUCCESS tables) | The run is FAILED and the watermark is held. The guard absorbs the replay. |
| `merge_rejects` | 1 MERGE | Same as `commit_state`. |
| Table log, watermark, run log | separate writes, `with_retry` | The watermark is written last, and only if every table is SUCCESS or NO_DATA. |

No step is atomic across two Delta tables. Correctness comes from the step order and from idempotency.

## Idempotency

- Replay: state marks the events stale. Any event that still reaches the MERGE loses or ties the guard, so business columns do not change.
- A replayed reject has the same `event_hash`. It increments `reject_count` and adds no row.
- `full_reload` with `table_filter` rebuilds one table. The guard keeps the newest version, and the watermark is not touched.
- Seeds insert only if absent, keyed by (`src_tbl`, `trg_tbl`[, `trg_column`]) and by `watermark_id`. Rerunning a seed is a no-op.

## Concurrency

- The lock is the `wm_transform_cms_raw_data` row. A second run ends `SKIPPED_CONCURRENT`.
- Partner and 3P use other watermark rows and other `src_tbl` partitions. Conflicts on shared ctrl tables are retried (`with_retry`).
- Each worker writes only its own target. The main thread does all ctrl writes.

## Retry and recovery

- A transient table error goes through `process_with_retry` (`max_retries = 1`). `CastNullError` is not retried: fix the registry or apply U6, then rerun.
- `VersionGapError`: run once with `allow_full_scan = True`.
- A stale lock is reclaimed after `running_timeout_minutes = 780`, and the old run becomes `ABANDONED`.

## Partial failure

- One table FAILED: the run is `PARTIAL_FAILED` and the watermark is held. SUCCESS tables commit their state and rejects. The next run re-reads the range: SUCCESS tables skip it through state, and the failed table reprocesses it.
- A commit fails after the target MERGEs: the targets are ahead of state, and replay is safe (I-7).
- Open payloads (about 60% of destination, D-09/D-11) become rejects and do not fail the run. About 137 destination keys and 17 blog keys have no closed event, so they are missing from silver (accepted, D-15 U1).

## Observability

- Exit JSON: the lib summary, plus `extra.docs_by_table`, `extra.ignored_detail` by `source_name`, and `extra.null_locale_rows` per table (counts only).
- `ctrl_log_table_run`: `input_rows`, `entity_rows`, inserted and updated counts, and `cast_null` detail by column. The B3 gate reads this.
- Operators use the 3P reject query with `src_tbl = 'cms_raw_data'`, grouped by `trg_tbl` and `reject_reason`.
- Logs carry counts and names only (I-10).

## Security

- Reject `after_payload` and the JSON-text columns copy signed URLs from bronze. The user accepted this (D-15 U3).
- Identifiers come from the validated registry and are quoted. No parameter value is concatenated into SQL. `sources` is compared through Column expressions. The guard literal is a constant.

## Rollout

1. DEV: run the `NB_CREATE_DDL` CMS patch cell. Check for 4 config rows, 48 registry rows (7 shared columns × 4 tables + 7 + 8 + 6 + 10 table-specific), and 1 watermark row.
2. Dry run: `dry_run = True, allow_full_scan = True, max_parallel = 4`. Compare `cast_null`, `docs_by_table`, rejects, and `null_locale_rows` with D-09, D-11, and D-12. **Gate (B3):** if `slv_cms_blog` has `cast_null > 0`, run P4 and get U6 before step 3.
3. Real run with `allow_full_scan = True`: about 193k events, with payloads up to 107 KB. Repartition after a FULL read (a known 3P issue).
4. Runs stay manual (D-03) until the user decides on a schedule.

## Rollback and forward recovery

- Stop: set the 4 config rows to `is_active = 0`. The notebook then has no specs and raises `ConfigError` before any write.
- DEV rollback: drop the 4 `slv_cms_*` tables, then delete the `src_tbl = 'cms_raw_data'` rows from config, registry, watermark, state, and reject. Partner and 3P are not affected.
- Forward: fix the registry, then run `full_reload = True, table_filter = <table>`. A new column (for example a D-17 "not modelled" key) needs a registry insert (the lib runs `ADD COLUMNS`) and then `full_reload`. A rename or type change also needs a manual `ALTER` or drop first.

## Implementation plan

| # | File | Anchor | Change |
|---|---|---|---|
| E1 | `notebooks/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb` (new) | parameters/constants cell | A1 constants, `TABLE_SOURCE`, `NULLABLE_KEYS`, `doc_key_column = "document_id"`, `state_key = "row"`, default `sources`, `cast_null_policy = "FAIL"`. No lang parameters. |
| E2 | same | `read_raw`, `classify_docs`, `presence`, `profile_docs` | A2, A3 |
| E3 | same | `build_table_rows`, `element_reject_rows` | A6 `needed` and key string |
| E4 | same | `resolve_latest`, `build_merge_sql` | A5 order, `#### Guard and ON clause` |
| E5 | same | `reject_frame`, `doc_source_payload`, `doc_reject_rows` | A3 identity |
| E6 | same | `build_context`, `check_config` | `ConfigError` rules (A2, A4, A5) |
| E7 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | new cell `init_cfg_cms` after `init_cfg_3p`; `init_plan` (`third_rows` line); `init_seed_ctrl` (`PIPELINE_CONFIG_ROWS`, watermark rows) | A8 `TABLE_CONFIGS_CMS`; `cms_rows = flatten_table_configs(TABLE_CONFIGS_CMS, _B, "cms_raw_data")`, `validate_rows`, `registry_rows += cms_rows`; 4 pipeline tuples; watermark `wm_transform_cms_raw_data` on `crawled_at` |
| E8 | `notebooks/NB_CREATE_DDL.ipynb` | new markdown and code cells at the end, `[THÊM 08/11] 20261104-extract-cms-raw-data` | Same rows, inserted if absent; `seed_registry(TABLE_CONFIGS_CMS, "lh_vv_bronze.dbo", "cms_raw_data")` |
| E9 | `tests/test_cms_l1_contract.py` (new) | — | Tests in Verification |
| E10 | `tests/test_initial_ddl_contract.py` | seed assertions | `test_cms_seed_rows_present` |
| E11 | `docs/context/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.md` (new) | 3P-doc section pattern | Flow, routing, A5, A6, A7 gate, operator query; counts and names only |
| E12 | `docs/context/CTRL_TABLES_CONTEXT.md` | `### Dữ liệu hiện có` in §3, §4, §5; §10 | CMS config, watermark, and registry summary; a history row |

## Verification

- `python -m pytest tests/test_cms_l1_contract.py tests/test_initial_ddl_contract.py tests/test_3p_l1_contract.py -q`
- `git diff --exit-code notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`
- `tests/test_cms_l1_contract.py` (static parsing, like the existing contract tests): `test_table_source_covers_all_four_tables`, `test_presence_routes_by_source_name`, `test_state_key_is_row_and_doc_key_is_document_id`, `test_no_type_or_lang_column_read`, `test_key_null_checks_document_id_only`, `test_merge_on_is_null_safe`, `test_merge_guard_orders_by_cms_updated_at_first`, `test_resolve_latest_orders_by_cms_updated_at_first`, `test_registry_keys_document_id_locale`, `test_cms_updated_at_active_on_all_tables`, `test_no_date_days_on_cms_registry`, `test_no_rule_on_locale`, `test_first_publish_date_is_date_none`, `test_registry_columns_match_model_design`, `test_config_rows_doc_mode_fl00`, `test_watermark_row_seeded`, `test_seed_cells_match_between_ddl_notebooks`.
- `tests/test_initial_ddl_contract.py`: `test_cms_seed_rows_present`.
- Runtime proof is not required. The DEV dry run with its B3 gate is recommended before the first real run.

## Required probes and decisions

None block implementation.

Probe P4 `cms-blog-time-nonmatch` is a rollout gate only. Run it if the dry run shows `cast_null > 0` on `slv_cms_blog`.
- Where: Fabric DEV, `lh_vv_bronze`, read only, aggregates only, with no values or URLs.
- Rows: `source_name = 'strapi_blog'` and `from_json(raw_payload, 'map<string,string>') IS NOT NULL`.
- For each of `createdAt`, `updatedAt`, `publishedAt`, and `first_publish_date`, count the rows where the key is absent, is JSON null, matches, or is present, non-null, and does not match.
- For non-matching values: the `length` and the shape `regexp_replace(regexp_replace(v,'[0-9]','9'),'[A-Za-z]','a')`, with counts, top 10.
- `locale`: counts of absent, null, blank, and value.
- Save the output to `evidence/results/cms-blog-time-nonmatch.md`.

User decision U6, only if P4 finds a malformed non-null value:
- (a) Keep `FAIL`.
- (b) Run with `cast_null_policy = WARN`.
- (c) Change the registry type or rule, then `full_reload` blog.

Recommended: (b) if there are 10 or fewer such values and they are all in one field.
