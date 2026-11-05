# Model design — 20261105-partner-hours-both-media-grain

## Scope

- Base task: `20261104-poi-review-src-and-partner-i18n`. This task was split from it after exec `c2a9f0ef-6d48-4241-b1fb-c9e25eddd4fe` (`decision.md` `## Lịch sử quyết định`). Parent evidence: `evidence/results/partner_multi_hours.txt` (8 failing i18n rows, max `hours` length 2) and `evidence/results/media_pk_duplicate.txt` (2 duplicate `media_id`, origin `i18n`, 3 rows each, same `poi_id`).
- Ledger rows implemented: `D-HOURS-2`, `D-MEDIA-KEY`, `D-MEDIA-TIE`, `D-GALLERY-KEY` (`decision.md` `## Quyết định hiện hành`).
- `proposal.md` does not exist in the task folder, so its `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` sections cannot be cited. This design rests on the ledger and the author-input constraints only. See Conflicts 1.
- Out of scope: `media_id` formulas, new output columns, a partner `hours` length above 2, and anything the Architect owns (MERGE semantics, idempotency, recovery, rollout).

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` | gold | one row per `poi_id` (unchanged). Inside `operating_hours`, partner days hold one object per `hours` interval: 1 object for length 1 or for closed days, 2 objects for length 2. | `NB_GLD_SRV_POI_INFO` |
| `lh_vv_silver.dbo.slv_poi_media_info` | silver | one row per (`media_id`, `poi_id`). Changed from `media_id` (`D-MEDIA-KEY`). | `NB_SLV_POI_MEDIA_INFO` |
| `lh_vv_gold.dbo.gld_srv_poi_media_gallery` | gold | one row per (`media_id`, `poi_id`), a 1-1 copy of silver. Changed from `media_id` (`D-GALLERY-KEY`). | `NB_GLD_SRV_POI_MEDIA_GALLERY` |

## Keys

**`gld_srv_poi_info`**
- Primary key: `poi_id` (`NodeSpec.pk=("poi_id",)`). No change.
- Business key: `poi_id`. Partner `poi_id = uuid_md5(id, lit('partner'))` per `AGENTS.md` §7 (8-4-4-4-12, `HASH_MD5_UUID` family). Google `poi_id` uses `uuid_format(md5(concat(source_name, source_id)))` per `AGENTS.md` §7.
- Foreign keys: none declared. `operating_hours` for partner rows is derived from `slv_poi_entity_non_enrich.opening_hours_text` on the same `poi_id` (`mapping_gld_srv_poi_info.md` §1.5).

**`slv_poi_media_info`**
- Primary key: (`media_id`, `poi_id`) (`D-MEDIA-KEY`). This replaces `pk=("media_id",)` in cell `slvmediabuild` and the MERGE-key sentence in `mapping_poi_media_info.md` §1.1.
- Business key, same columns:
  - Partner `media_id = sha2(concat_ws('|', 'partner', poi_id, trim(media.url)), 256)`, from i18n or from the services fallback. The formula is unchanged (`mapping_poi_media_info.md` §1.2; cell `slvmediabuild` `partner_media`).
  - Google `media_id = slv_3p_poi_media.media_dedup_key`, copied 1-1.
  - Partner `poi_id = uuid_md5(business_service_id, 'partner')` (`mapping_poi_media_info.md` §1.2 row `poi_id`; `AGENTS.md` §7).
  - Google `poi_id`: `slv_3p_poi_media.poi_id`, copied 1-1 (`HASH_MD5_UUID` per `AGENTS.md` §7).
- Pre-gate collapse key: (`media_id`, `poi_id`). The build keeps the row with the largest parent technical `updated_at` (`D-MEDIA-KEY`). Ties go to a fixed total order (see Columns, internal ranking rows; `D-MEDIA-TIE`).
- Foreign keys (logical, not enforced): `poi_id` points to the POI identity of the source. Partner rows trace to `slv_pn_business_service_i18ns.business_service_id` and `slv_pn_business_services.id`.

**`gld_srv_poi_media_gallery`**
- Primary key: (`media_id`, `poi_id`) (`D-GALLERY-KEY`). This replaces `pk=("media_id",)` in the gallery `NodeSpec` and the MERGE-key sentence in `mapping_poi_media_info.md` §2.
- Business key: the same columns, taken unchanged from `slv_poi_media_info`.
- Foreign key (logical): (`media_id`, `poi_id`) → `slv_poi_media_info` (`media_id`, `poi_id`).

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_srv_poi_info` | `operating_hours` | string (JSON array) | yes; null when `opening_hours_text` is null (§1.5) | `slv_poi_entity_non_enrich.opening_hours_text`, partner object `$.<day>.hours` | `D-HOURS-2`. For a day whose `hours` has 2 elements, emit 2 objects with that day's `day_of_week`, in source array order (`hours[0]`, then `hours[1]`). Each object keeps today's single-interval shape: `day_of_week`, `label`, `value` = `open_time` + ` - ` + `close_time`, `open_time`, `close_time`, `is_open_all_day = false`, `is_closed = false`. Each element is checked like today: it must be a dict and both times must be strings, else `PARTNER_BAD_HOURS`. Length 2 does not raise `PARTNER_MULTI_HOURS`. Length 0 or 1, a missing day key, and a missing `hours` key keep §1.5 unchanged. Days stay ordered Monday → Sunday (§1.5). This replaces §1.5 line "Nhiều hơn một phần tử `hours`… dừng `PARTNER_MULTI_HOURS`" and the `len(hours) > 1` branch of `partner_hours`. |
| `slv_poi_media_info` | `media_id` | string | no; `STRING NOT NULL` (§1.1) | §1.2 row `media_id` | Formula unchanged. Becomes part of the composite pk (`D-MEDIA-KEY`). |
| `slv_poi_media_info` | `poi_id` | string | no; already blocked by `media_required_null` (`poi_id IS NULL`) | §1.2 row `poi_id` | Formula unchanged. Becomes part of the composite pk (`D-MEDIA-KEY`). |
| `slv_poi_media_info` | `is_cover` | boolean | no | derived | Rule unchanged (§1.2 row `is_cover`). Computed by `with_cover` over the collapsed rows, after the collapse, so `one_cover_per_poi` holds on what is written. The kept row's `_pos` is used in the order. |
| `slv_poi_media_info` | internal ranking column (underscore-prefixed, dropped by `select(*OUT_COLS)`; Main picks the name) | timestamp | see Conflicts 4 | partner: technical `updated_at` of the parent row whose `media` array was exploded (`TECH_COLUMNS`, `NB_LIB_EXTRACT_RAWDATA.md` §1). Google: see Conflicts 3. | `D-MEDIA-KEY`. Copy the parent `updated_at` onto every element `posexplode` produces, so elements from one parent share it. Use the technical `updated_at` only, never `src_updated_at` or `last_updated_at` (`decision.md` `## Lịch sử quyết định`). It is not an output column. Output `updated_at` stays the `sql_merge_target` technical column (§1.2). |
| `slv_poi_media_info` | collapse order (no column) | — | — | columns the build already has | `D-MEDIA-KEY` + `D-MEDIA-TIE`. Partition by (`media_id`, `poi_id`) and keep `row_number = 1` with this order: parent `updated_at` desc, then `display_order` asc nulls last, then `_pos` asc nulls last, then `blob_url` asc nulls last, then `photo_api_uri`, `width_px`, `height_px`, `photographer` asc nulls last. Rows still tied after this agree on every column in `OUT_COLS` except `is_cover`, which is computed afterwards. So the output is the same on every rerun, while still "any tied row" in the sense of `D-MEDIA-TIE`. |
| `gld_srv_poi_media_gallery` | `media_id` | string | no | `slv_poi_media_info.media_id` | Copied 1-1. Part of the composite pk (`D-GALLERY-KEY`). |
| `gld_srv_poi_media_gallery` | `poi_id` | string | see Conflicts 5 | `slv_poi_media_info.poi_id` | Copied 1-1. Part of the composite pk (`D-GALLERY-KEY`). |

No columns are added to or removed from any `OUT_COLS`.

## Lineage

**`gld_srv_poi_info`**
- Bronze: none read directly.
- Silver: `slv_poi_entity_non_enrich` (`opening_hours_text`), `slv_enr_poi_destination`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review` (`NodeSpec.inputs`). Unchanged.
- Gold: none.

**`slv_poi_media_info`**
- Bronze: none read directly.
- Silver: `slv_3p_poi_media` (`media_3p`), `slv_pn_business_service_i18ns` (`i18n`, `locale = 'vi'`, live rows), `slv_pn_business_services` (`services`, live rows). Unchanged inputs. Now also reads each input's technical `updated_at`; see Conflicts 3.
- Gold: none.

**`gld_srv_poi_media_gallery`**
- Bronze: none.
- Silver: `slv_poi_media_info` only.
- Gold: none. It does not read gold.

## Conflicts and questions

1. `proposal.md`, `problem-analysis.md`, and `requirements-analysis.md` are missing from the task folder, so the `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` citations the handoff asks for cannot be made. Should a proposal be authored first, or does the ledger replace it for this task?
2. Three mapping texts conflict with the ledger and need Main's update:
   - `mapping_gld_srv_poi_info.md` §1.5 ("Nhiều hơn một phần tử `hours`… `PARTNER_MULTI_HOURS`")
   - `mapping_poi_media_info.md` §1.1 ("Khóa MERGE … là `media_id`")
   - `mapping_poi_media_info.md` §2 ("Khóa MERGE `media_id`")

   The notebook markdown cell `slvmediamd` ("Khóa `media_id`") also needs the change.
3. Google media `updated_at`:
   - `MEDIA_3P_COLS` and `_require` in `slvmediabuild` do not include `updated_at`. The files read do not show whether `slv_3p_poi_media` carries `TECH_COLUMNS` or `SNAPSHOT_TECH_COLUMNS` `updated_at`.
   - Confirm that column exists and that the collapse covers Google rows. If Google rows are exempt, say which rule applies to them.
   - Partner `media_id` hashes `poi_id`, so the new pk only changes behaviour for Google if one `media_dedup_key` appears under more than one `poi_id`. That is unknown.
4. Partner parent `updated_at`:
   - Proposed: `i18n.updated_at` when the i18n `media` is used, `services.updated_at` when the services fallback is taken (the row whose array was exploded). Please confirm.
   - The nullability of the technical `updated_at` is not shown. This design puts nulls last, below any non-null value. Confirm, or name a different rule (for example `MIN_TS`, as the extract library does).
5. Target DDL: the files read do not show whether the Delta table or the `NB_SETUP_INITIAL_DDL` / `NB_CREATE_DDL` definitions declare `poi_id` NOT NULL or record the pk for `slv_poi_media_info` and `gld_srv_poi_media_gallery`. They also do not show whether `ctrl_cfg_schema_registry` stores pk or key columns that must change. This needs evidence or a proposal line.
6. The duplicate evidence shows 3 rows per `media_id` but does not say whether they come from 3 i18n `vi` rows for one `business_service_id` or from one `media` array repeating a URL. The collapse order above covers both cases. Whether a source-side duplicate warning or metric is wanted is not stated.
7. A partner `hours` length above 2 is out of scope. This design keeps the existing `PARTNER_MULTI_HOURS` stop for length > 2 only. Confirm, or state the intended behaviour.
