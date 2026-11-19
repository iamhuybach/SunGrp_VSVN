# Model design — 20261119-gsm-as-google-extract

## Scope

- Base task: `20261119-gsm-as-google-extract`. Bronze rows with `source_name = 'sgm'` go through the current Google 3P path. There is no new extract notebook, pipeline, table, column, or dictionary source (`decision.md` `## Quyết định của người dùng` D-1).
- Ledger rows implemented: D-1 (sgm identity), D-2 (MERGE key collision, 402 overlapping `source_id`), D-3 (google priority).
- Proposal: none. The handoff says there is no `proposal.md`, so this design cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. Every rule below cites a ledger row, an evidence file, or a context doc instead. See Conflicts item 1.
- Evidence used: `evidence/results/p1_sgm_source_id.txt` and `evidence/payload-shape.md`. `model-design.void-gsm.md` is not used.
- Out of model scope (Architect or Main): ordering, the state or `entity_key` mechanics behind "does not MERGE", watermarks, idempotency, backfill of the 402 keys, and the FL_00 `sources` parameter value. `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §4 says the default is `google` and other names are IGNORED `OUT_OF_SCOPE`.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `slv_3p_poi` | silver L1 | one row per `poi_id` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_address` | silver L1 | one row per `poi_id` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_contact` | silver L1 | one row per `poi_id` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_price` | silver L1 | one row per `poi_id` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_opening_hours` | silver L1 | one row per `poi_id` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_rating` | silver L1 | one row per `poi_id` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_amenity` | silver L1 | one row per `poi_id` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_review` | silver L1 | one row per `review_id` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_media` | silver L1 | one row per `media_dedup_key` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_poi_entity_non_enrich` | silver L2 | one row per `poi_id` (active grain unchanged, per the handoff constraint) | `NB_SLV_POI_ENTITY_NON_ENRICH` |
| `slv_poi_amenity` | silver L2 | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | `NB_SLV_POI_AMENITY` |
| `slv_poi_media_info` | silver L2 | (`media_id`, `poi_id`) | `NB_SLV_POI_MEDIA_INFO` |
| `gld_srv_poi_info` | gold | one row per `poi_id` | `NB_GLD_SRV_POI_INFO` |
| `gld_srv_poi_multi_lang` | gold | (`poi_id`, `lang`) | `NB_GLD_SRV_POI_MULTI_LANG` |
| `gld_srv_poi_review` | gold | one row per `review_id` | `NB_GLD_SRV_POI_REVIEW` |
| `gld_srv_poi_amenity` | gold | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | `NB_GLD_SRV_POI_AMENITY` |
| `gld_srv_poi_media_gallery` | gold | (`media_id`, `poi_id`) | not shown in the files read |
| `gld_enr_poi_info` | gold (`lh_vv_gold.enr`) | one row per `poi_id` (`NB_CREATE_DDL` `TARGETS`) | `NB_ENR_POI_INFO` |

## Keys

**Identity formula.** Third-party `poi_id = uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`). This is `AGENTS.md` §7, `docs/context/01_DATA_MODEL.md` §5.2 and §8, and `NB_CREATE_DDL` cell 14 `POI_ID = {"path": "_doc.source_name,_doc.source_id", "rule": "HASH_MD5_UUID"}`.

**Change from D-1.** For a bronze row with `source_name = 'sgm'`, `poi_id = HASH_MD5_UUID('google', source_id)`. Rows with bronze `source_name = 'google'` keep their current formula and value. No `poi_id` is ever derived from `'sgm'`. `source_id` comes from the bronze column `_doc.source_id` (`RAW_DOC_ID`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §5). It does not come from payload `id`. The probe result `id_eq_source_id=2630` is not used as a key source. How the registry expresses the literal `'google'` is an open question (Conflicts item 2).

| table | primary key | business key | foreign keys |
|---|---|---|---|
| `slv_3p_poi` | `poi_id` | (effective source, `source_id`), where effective source is `'google'` for both bronze names (D-1) | none |
| `slv_3p_poi_address`, `_contact`, `_price`, `_opening_hours`, `_rating`, `_amenity` | `poi_id` | same as `slv_3p_poi` | `poi_id` → `slv_3p_poi.poi_id` (logical) |
| `slv_3p_poi_review` | `review_id` = `HASH_SHA256(_doc.source_name, _doc.source_id, authorAttribution.displayName, publishTime)` (cell 14) | unchanged | `poi_id` → `slv_3p_poi.poi_id` |
| `slv_3p_poi_media` | `media_dedup_key` = `HASH_SHA256_PIPE(_doc.source_name, _doc.source_id, name)` (cell 14) | unchanged | `poi_id` → `slv_3p_poi.poi_id` |
| `slv_poi_entity_non_enrich` | `poi_id` | unchanged | `poi_id` ← `slv_3p_poi.poi_id` |
| `slv_poi_amenity` | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | unchanged | `poi_id` ← `slv_3p_poi_amenity.poi_id` (`mapping_gld_srv_poi_amenity.md` §0) |
| `slv_poi_media_info` | (`media_id`, `poi_id`) | unchanged | Google rows ← `slv_3p_poi_media` (`mapping_poi_media_info.md` §1.1) |
| `gld_srv_poi_info` | `poi_id` | unchanged | ← `slv_poi_entity_non_enrich.poi_id` |
| `gld_srv_poi_multi_lang` | (`poi_id`, `lang`) | unchanged | ← `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich` |
| `gld_srv_poi_review` | `review_id` | unchanged | ← `slv_3p_poi_review` |
| `gld_srv_poi_amenity` | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | unchanged | ← `slv_poi_amenity` |
| `gld_srv_poi_media_gallery` | (`media_id`, `poi_id`) | unchanged | ← `slv_poi_media_info` |
| `gld_enr_poi_info` | `poi_id` | unchanged | ← silver inputs in `CTRL_TABLES_CONTEXT.md` §3 |

Under D-1, a bronze `sgm` row and a bronze `google` row with the same `source_id` get the same `poi_id`. Probe `overlap_source_id=402` shows 402 such pairs (D-2). Every `poi_id`-keyed table keeps one row per `poi_id`. D-3 decides which bronze source fills that row.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_3p_poi` | `poi_id` | string | not shown in the files read | `_doc.source_name`, `_doc.source_id` | Bronze `google`: `HASH_MD5_UUID(source_name, source_id)`, value unchanged. Bronze `sgm`: `HASH_MD5_UUID('google', source_id)` (D-1). |
| `slv_3p_poi` | `source_name` | string | not shown | `_doc.source_name` | Stores the bronze value `sgm` or `google` (D-1). An sgm-only `source_id` stores `sgm` (D-3). A google event newer than a stored `sgm` row writes `google` (D-3). An sgm event newer than a stored `google` row does not MERGE (D-3). |
| `slv_3p_poi` | `source_id` | string | not shown | `_doc.source_id` | 1-1, unchanged. Not taken from payload `id`. |
| `slv_3p_poi_address`, `_contact`, `_price`, `_opening_hours`, `_rating`, `_amenity` | `poi_id` | string | not shown | `POI_ID` | Same derivation as `slv_3p_poi.poi_id` (D-1). |
| `slv_3p_poi_review` | `poi_id` | string | not shown | `POI_ID` | Same derivation (D-1). |
| `slv_3p_poi_review` | `review_id` | string | not shown | `_doc.source_name, _doc.source_id, authorAttribution.displayName, publishTime` | Unchanged formula (cell 14). It still hashes the bronze `source_name` (D-2). See Conflicts item 4. |
| `slv_3p_poi_media` | `poi_id` | string | not shown | `POI_ID` | Same derivation (D-1). |
| `slv_3p_poi_media` | `media_dedup_key` | string | `MISSING` (`mapping_poi_media_info.md` §1.1) | `_doc.source_name, _doc.source_id, name` | Unchanged formula (cell 14). It still hashes the bronze `source_name` (D-2). See Conflicts item 4. |
| `slv_poi_entity_non_enrich` | `source_name` | string | not shown | `slv_3p_poi.source_name` (exact upstream expression not shown) | Effective value: `'google'` when the upstream value is `'sgm'`; otherwise unchanged (D-1, author input). This is the shared silver decision that gold relies on. |
| `slv_poi_amenity` | (dictionary lookup) | — | — | `ref_dictionary_amenities` | An `sgm` row uses the existing `source_name = google` dictionary rows. No `sgm` dictionary is added (D-1 user decision). No new column. |
| `slv_poi_media_info` | `source_name` | string | not shown | `slv_3p_poi_media` | Already `google` for every `slv_3p_poi_media` row (`mapping_poi_media_info.md` §1.2). No change. |
| `gld_srv_poi_info` | `source_name` | string | not shown | `slv_poi_entity_non_enrich.source_name` | 1-1 (`mapping_gld_srv_poi_info.md` §1.2). Gets `google` for sgm rows through the entity rule, so the existing `google` filter, the rating and review join, and the `SOURCE_NOT_GOOGLE_PARTNER` check need no new value. |
| `gld_srv_poi_multi_lang` | `source_name` | string | not shown | `slv_poi_entity_non_enrich.source_name` (P1) | 1-1 (`mapping_gld_srv_poi_multi_lang.md` §1.2). Gets `google` for sgm rows through the entity rule. |
| `gld_srv_poi_review` | `source_name` | string | not shown | literal | Literal `'google'` (`mapping_gld_srv_poi_review.md`, mapping D-3). No change. |

Registry content columns are not changed. Payload keys outside the Google registry contract, for example `x_lodging`, `x_scraper`, `internationalPhoneNumber` and `googleMapsLinks` (`payload-shape.md`), get no `json_path` (D-1 user decision).

## Lineage

- `slv_3p_poi` and its 8 child tables: bronze `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` (`normalized_payload` and `_doc` columns `source_name`, `source_id`, `language_code`; order column `crawled_at`) → `lh_vv_silver.dbo.slv_3p_poi*` through `ctrl_cfg_schema_registry` rows seeded from `TABLE_CONFIGS_3P`. The table list matches `CTRL_TABLES_CONTEXT.md` §3 FL_00 3P rows.
- `slv_poi_entity_non_enrich`: silver `slv_3p_poi` and other `slv_3p_poi_*` inputs (6 entity edges per `CTRL_TABLES_CONTEXT.md` change log 20/10) plus partner silver. The exact edge list is not in the files read.
- `slv_poi_amenity`: silver `slv_3p_poi_amenity`, `slv_poi_entity_non_enrich`, `ref_dictionary_amenities`, `slv_pn_business_services`, `slv_pn_business_service_i18ns`.
- `slv_poi_media_info`: silver `slv_3p_poi_media`, `slv_pn_business_service_i18ns`, `slv_pn_business_services`.
- `gld_srv_poi_info`: silver `slv_poi_entity_non_enrich`, `slv_enr_poi_destination`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review`, `slv_poi_media_info`.
- `gld_srv_poi_multi_lang`: silver `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, `slv_pn_business_service_i18ns`.
- `gld_srv_poi_review`: silver `slv_3p_poi_review`, `slv_3p_poi_rating`.
- `gld_srv_poi_amenity`: silver `slv_poi_amenity`.
- `gld_srv_poi_media_gallery`: silver `slv_poi_media_info`.
- `gld_enr_poi_info`: silver `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns`.
- No gold table reads another gold table.

## Conflicts and questions

1. There is no `proposal.md`. The handoff asks this design to cite `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`, but those sections do not exist. The registry change that sets `poi_id` for sgm rows has no proposal to cite.
2. The registry cannot express the D-1 `poi_id` yet. `POI_ID` path `_doc.source_name,_doc.source_id` hashes the bronze value. The files read do not show that `HASH_MD5_UUID` accepts a literal part such as `'google'`, or any rule that maps `sgm` to `google` before hashing. Which mechanism produces `HASH_MD5_UUID('google', source_id)` for bronze `sgm`: a registry path or rule change, or an extract code change? It must not invent a `json_path` or rule.
3. The equal `crawled_at` case is unstated. D-3 covers an sgm event newer than a `google` row and a google event newer than an `sgm` row. It does not say what happens when both have the same `crawled_at`. No tie-break is chosen here.
4. Leftover `review_id` and `media_dedup_key` rows. Both still hash bronze `_doc.source_name` (D-2). After an `sgm` row exists and a newer google event is written for the same `poi_id`, the google event creates new `review_id` and `media_dedup_key` values hashed with `'google'`. The rows hashed with `'sgm'` stay, because the MERGE does not physically delete review rows (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §5) and child tables only upsert (`01_DATA_MODEL.md` §5.2). Effects downstream: duplicate reviews in `gld_srv_poi_review`, an inflated `review_count` in `gld_srv_poi_info`, extra media rows in `slv_poi_media_info` and `gld_srv_poi_media_gallery`, and possibly a different `is_cover` pick. Should these two keys also hash `'google'` for sgm rows, should sgm-keyed rows be retired, or is the duplication accepted? No resolution is chosen here.
5. Does D-3 apply to every table? D-3 is stated for `slv_3p_poi.source_name`. Must "does not MERGE" and "google wins" apply the same way to the 6 `poi_id`-keyed child tables and to `slv_3p_poi_review` and `slv_3p_poi_media`? With `state_key = doc` the `entity_key` is `poi_id` for every table (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §4), but which mechanism enforces it is the Architect's call.
6. A google event older than a stored `sgm` row is unstated. D-3 only covers a google event newer than an `sgm` row. Is an older google event skipped, as the general late-arrival rule would do, or does google priority still apply?
7. The 402 overlapping keys have no dated state. The probe does not say how many of the 402 already exist on `slv_3p_poi` (`silver_sgm=0`, `silver_google=20537`) or which side has the newer `crawled_at` (`decision.md` `## Giả định còn lại`). So the share of the 402 that D-3 resolves as "skip sgm" versus "sgm stored, later google" is unknown.
8. The two evidence files disagree on key presence. `payload-shape.md` lists `servesBreakfast` … `curbsidePickup` as absent from its single document. `p1_sgm_source_id.txt` reports `absent=0` and `present_null=2630` for the same keys across all 2630 sgm rows. Which is correct? This decides whether sgm amenity flags are JSON null or missing. No `json_path` is added either way.
9. Where does the effective `source_name` get applied? D-1 puts it after `slv_3p_poi`. This design puts the `sgm` → `google` mapping on `slv_poi_entity_non_enrich.source_name` (silver, shared rule). The current source expression of that column is not in the files read. Is that the only place it belongs? Does `NB_SLV_POI_AMENITY` or `NB_ENR_POI_INFO` read `source_name` from another source that would also need it?
10. `gld_srv_poi_media_gallery` has no node notebook name in the files read.
11. The documents disagree on registry counts: 98 columns (83 on) in `CTRL_TABLES_CONTEXT.md` and `01_DATA_MODEL.md`, against 9 tables and 53 columns in `NB_CREATE_DDL` cell 14 and the 19/10 notes. This design changes no content column. The difference is noted only so a reviewer can check which count the registry seed validation expects.
