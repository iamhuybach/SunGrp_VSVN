# Model design: 20261119-gsm-as-google-extract

## Scope

- Base task: `20261119-gsm-as-google-extract`. `task-state.yaml` lists the status as `waiting_architecture` and the gate `architecture: evidence_required`.
- There is no `proposal.md` for this task. Because of that, this design cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. See Conflicts and questions item 1.
- Ledger rows implemented (`decision.md` `## Quyết định hiện hành`):
  - D-1: `slv_3p_poi` stores the bronze `source_name` (`sgm` or `google`). Downstream of `slv_3p_poi`, the effective `source_name` of an `sgm` row is `google`, and `poi_id = HASH_MD5_UUID('google', source_id)`. There is no second `poi_id` from `sgm`.
  - D-2: 402 `source_id` values overlap between `sgm` and `google` and collide on the MERGE key `poi_id`.
  - D-3: `google` has priority. A newer `sgm` event does not MERGE onto a row whose `source_name` is `google`. An `sgm`-only `source_id` stores `source_name = sgm` with the D-1 `poi_id`.
  - D-4 (option B): for an `sgm` event, `review_id` and `media_dedup_key` hash the effective `source_name` `google`, not the bronze `sgm`. Rows from `google` keep their current key formulas. `sgm` photos whose names do not match a `google` photo stay as separate rows.
  - D-5 (override): a `google` event whose `crawled_at` is older than a stored `sgm` row still MERGEs, and `source_name` becomes `google`.
- Evidence used: `evidence/results/p2_sgm_overlap_detail.txt`. `NAME` values are exactly `google` and `sgm`. The other counts are `overlap_exact = overlap_trimmed = 402`, `silver_hit = 402`, `sgm_newer = 402`, `google_newer = 0`, `equal = 0`, `sgm_only = 2228`, `sgm_reviews = 2041`, `match_exact = 93`, `sgm_photos = 2814`, `match_name = 0` and `scraper_named = 2814`.
- Out of scope: ordering, tie-break, idempotency and commit boundaries. These belong to the Architect. This design states only how D-5 affects keys.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `slv_3p_poi` | silver L1 | one row per `poi_id`. Because of D-1, one row per third-party `source_id` across `google` and `sgm` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_review` | silver L1 | one row per `review_id` (registry `key`, `NB_CREATE_DDL` cell 14, `source_table` `reviews`) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_3p_poi_media` | silver L1 | one row per `media_dedup_key` (registry `key`, `NB_CREATE_DDL` cell 14, `source_table` `photos`) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |

The node notebook comes from the `scope.files` list in `task-state.yaml`. The files I read do not show which downstream silver L2 and gold tables change (see Conflicts and questions item 5).

## Keys

`slv_3p_poi`
- Primary key / MERGE key: `poi_id`.
- Formula: `poi_id = HASH_MD5_UUID(source_name, source_id)`, defined in `docs/context/01_DATA_MODEL.md` §8 as `uuid_format(md5(source_name ‖ source_id))`. Under D-1, the effective `source_name` is the literal `'google'` for both `google` and `sgm` events. So `poi_id = HASH_MD5_UUID('google', source_id)`.
- Business key: `source_id`. Because of D-1, the stored bronze `source_name` is not part of the key.
- Key effect of D-3 and D-5: a `google` event lands on the same `poi_id` as an existing `sgm` row and replaces it, regardless of `crawled_at` (D-5). An `sgm` event lands on the same `poi_id` as an existing `google` row and does not MERGE (D-3). Both events share a single `poi_id`. Neither creates a second key.

`slv_3p_poi_review`
- Primary key / MERGE key: `review_id`, rule `HASH_SHA256`. §8: `sha2(concat(...), 256)`.
- Current registry path (`NB_CREATE_DDL` cell 14): `_doc.source_name, _doc.source_id, authorAttribution.displayName, publishTime`.
- Change (D-4 B):
  - `google` event: no change. `review_id = HASH_SHA256(_doc.source_name, _doc.source_id, authorAttribution.displayName, publishTime)`, where `_doc.source_name = google`.
  - `sgm` event: the first component is the literal `google` instead of the bronze `_doc.source_name`. `review_id = HASH_SHA256('google', _doc.source_id, authorAttribution.displayName, publishTime)`.
  - Result: an `sgm` review and a `google` review with the same `source_id`, `authorAttribution.displayName` and `publishTime` produce the same `review_id`. p2 found `match_exact = 93` of `sgm_reviews = 2041`. Reviews that differ in any hashed component stay as separate rows.
- Foreign key: `poi_id` → `slv_3p_poi.poi_id`. The value is `POI_ID`, the same D-1 formula.
- No new column. The registry entry does not show how the literal is substituted (see Conflicts and questions item 2).

`slv_3p_poi_media`
- Primary key / MERGE key: `media_dedup_key`, rule `HASH_SHA256_PIPE`. §8: `sha2(concat_ws('|', trim(...)), 256)`.
- Current registry path (`NB_CREATE_DDL` cell 14): `_doc.source_name, _doc.source_id, name`.
- Change (D-4 B):
  - `google` event: no change. `media_dedup_key = HASH_SHA256_PIPE(_doc.source_name, _doc.source_id, name)`.
  - `sgm` event: `media_dedup_key = HASH_SHA256_PIPE('google', _doc.source_id, name)`.
  - Result: p2 found `match_name = 0` and `scraper_named = 2814` of `sgm_photos = 2814`. So no `sgm` photo currently collides with a `google` photo, and every `sgm` photo stays as its own row under the shared `poi_id` (D-4).
- Foreign key: `poi_id` → `slv_3p_poi.poi_id` (`POI_ID`, the D-1 formula).
- No new column.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_3p_poi` | `poi_id` | not shown in the sections read (see Q4) | not shown in the sections read (see Q4) | `_doc.source_id`, with literal `'google'` | `HASH_MD5_UUID('google', source_id)` for both `google` and `sgm` events (ledger D-1, §8) |
| `slv_3p_poi` | `source_name` | not shown in the sections read (see Q4) | not shown in the sections read (see Q4) | bronze `_doc.source_name` | stores the bronze value `sgm` or `google` (D-1). `sgm` only when no `google` event has written the `poi_id` (D-3). Becomes `google` when a `google` event MERGEs, including an older one (D-5) |
| `slv_3p_poi_review` | `review_id` | `string` (registry) | not shown in the sections read (see Q4) | `google`: `_doc.source_name, _doc.source_id, authorAttribution.displayName, publishTime`. `sgm`: literal `google`, `_doc.source_id, authorAttribution.displayName, publishTime` | `HASH_SHA256`. The literal `google` replaces bronze `source_name` for `sgm` events only (D-4 B) |
| `slv_3p_poi_review` | `poi_id` | not shown in the sections read (see Q4) | not shown in the sections read (see Q4) | `POI_ID` | D-1 formula |
| `slv_3p_poi_media` | `media_dedup_key` | `string` (registry) | not shown in the sections read (see Q4) | `google`: `_doc.source_name, _doc.source_id, name`. `sgm`: literal `google`, `_doc.source_id, name` | `HASH_SHA256_PIPE`. The literal `google` replaces bronze `source_name` for `sgm` events only (D-4 B) |
| `slv_3p_poi_media` | `poi_id` | not shown in the sections read (see Q4) | not shown in the sections read (see Q4) | `POI_ID` | D-1 formula |

No column is added (author input, D-4).

## Lineage

- `slv_3p_poi`, `slv_3p_poi_review` and `slv_3p_poi_media`:
  - Bronze: the third-party bronze raw rows whose `NAME` is `google` or `sgm` (p2 `NAME` lines). The sections I read do not name the bronze table (see Q5).
  - Silver: `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` writes them. Under D-3, the extract also reads the existing `slv_3p_poi` row for the same `poi_id` to decide whether an `sgm` event may MERGE. That read is implied by p2 `silver_hit = 402`. The Architect owns how and when it happens.
  - Gold: none read by these tables.
- Downstream silver L2 and gold tables: `task-state.yaml` lists `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_SLV_POI_AMENITY`, `NB_SLV_POI_MEDIA_INFO`, `NB_ENR_POI_INFO` and `NB_GLD_SRV_POI_INFO`. The files in scope for this run do not show their reads. Gold must read silver, not gold.

## Conflicts and questions

1. There is no `proposal.md`. This design cannot cite `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`, so the registry change for the two key columns has no accepted proposal text behind it. Should a proposal be written first, or does the ledger (D-1 to D-5) serve as the accepted source?
2. Mechanism for the literal `google`: the registry `path` is a column list (`_doc.source_name, ...`), and cell 14 shows no conditional form. Will the effective `source_name` be resolved once upstream, for example by normalising `_doc.source_name` to `google` before hashing while `slv_3p_poi.source_name` keeps the bronze value? Or will the registry `path` or `rule` change? This design adds no column and invents no path or rule.
3. Equal `crawled_at` between a `google` event and a stored `sgm` row, or between an `sgm` event and a stored `google` row: the ledger does not state the outcome. D-3 covers "newer `sgm`", and D-5 covers "older `google`". p2 shows `equal = 0` on today's data. I do not choose a tie-break here. That decision belongs to the Architect or the user.
4. The `poi_id` and `source_name` types on `slv_3p_poi`, and nullability on all affected columns, do not appear in the sections I read. Registry types are shown only for `review_id` and `media_dedup_key` (`string`). Please confirm them from the DDL.
5. The sections I read name neither the bronze source table nor the downstream silver L2 and gold reads. Do any downstream nodes (for example, the `mapping_*` docs in `task-state.yaml` scope) hash or filter on `source_name` and need the D-1 effective value? Each needs a row in this design once confirmed.
6. Existing rows: if an `sgm`-only row was stored with keys hashed on bronze `sgm` before D-4, its `review_id` and `media_dedup_key` will not match the new formula. p2 shows `silver_sgm = 0` per the ledger history, so there may be no such rows. Please confirm before the run.
