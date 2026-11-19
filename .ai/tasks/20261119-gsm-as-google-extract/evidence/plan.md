# Evidence plan

## Decision to resolve

Whether a `sgm` bronze row and a `google` bronze row share `source_id`. `slv_3p_poi` and the child `slv_3p_poi_*` tables MERGE on `poi_id`. The fixed identity sets a `sgm` row's `poi_id` to `HASH_MD5_UUID('google', source_id)`, which is `md5(concat('google', source_id))` in UUID form (`NB_LIB_EXTRACT_RAWDATA` `derived_sql`). The same `source_id` is therefore the same MERGE key as the existing `google` row. The UPDATE writes `source_name` from the incoming event, so a newer `crawled_at` can change an existing `google` row's `source_name` to `sgm`.

`review_id` is `sha2(concat(source_name, source_id, authorAttribution.displayName, publishTime), 256)`. `media_dedup_key` is `sha2(concat_ws('|', trim(source_name), trim(source_id), trim(name)), 256)`. Both paths start with `_doc.source_name`. Using bronze `sgm` in those hashes makes a second key. Using `google` makes the same key as the Google row.

Also resolve, without printing values:

- Whether `normalized_payload.id` equals bronze `source_id` on `sgm` rows. The repository contract does not say that it does.
- For each active registry top-level key, whether `sgm` documents omit the key or store JSON null. `profile_docs` uses `json_object_keys`. A present null key is not a missing field. `JSON_PICK` keeps a key when it is in `_top_keys`.

## Existing evidence

- Notebook parameter `sources` default is `google` (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` cell 1). Classification sends any other `source_name` to `IGNORED` / `OUT_OF_SCOPE` (cell 6).
- Pipeline activity `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` in `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json` passes `sources` value `google`. That parameter is not in `ctrl_mng_pipeline_config`. No DEV probe for it.
- `poi_id` path is `_doc.source_name,_doc.source_id` with `HASH_MD5_UUID` (`NB_CREATE_DDL` cell 14). `source_name` on `slv_3p_poi` is `_doc.source_name`.
- Active targets and modes are the nine `DOC` / `DOC_ARRAY` rows in `docs/context/CTRL_TABLES_CONTEXT.md` for `brz_3rd_crawler_poi_stream`. `slv_3p_poi_policy` is not in that active list.
- One `sgm` document is recorded in `evidence/payload-shape.md`. It does not show overlap, `source_id`, or a distribution of nulls.
- `evidence/results/p1_gsm_source_id.txt` filtered `source_name = 'gsm'`. The user corrected the source to `sgm`. That file does not answer this plan. `model-design.void-gsm.md` is the model written from that filter and is not `model-design.md`.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `p1_sgm_source_id.py` | Fabric DEV, read-only | Overlap of trimmed `source_id` between `sgm` and `google`; counts only for payload `id` versus `source_id`; registry top-level key absent vs JSON null vs present on `sgm` rows | `overlap_source_id > 0`: stop at `user_decision`, no code change. `overlap_source_id = 0`: current google rows are not the same MERGE key. Either result still leaves key-state counts as input to architecture. | `evidence/results/p1_sgm_source_id.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
- Do not print `source_id`, payload text, names, phone numbers, or URLs.
