You are the proposal author for VSVN task `20261013-3p-extract-from-raw-payload`. This is not an Architect turn. Do not write `architecture.md`. Do not edit, create, or delete any file. Read the repository and return two document bodies in the structured JSON result.

Set `model` to `claude-opus-5-5` and `effort` to `medium`. Do not infer effort from a numeric reasoning budget, and do not return empty documents because a budget number looks low. Complete both documents.

## Change under proposal

The 3rd-party extract would stop reading `normalized_payload`. It would read `raw_payload` of `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`. `normalized_payload` would be dropped in a later task. This turn does not drop that column and does not change code.

`notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` currently sets `RAW_PAYLOAD` to `normalized_payload`.

## Read these sources

- `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`
- `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`
- `docs/context/01_DATA_MODEL.md`, silver L1 3rd-party section
- `notebooks/NB_CREATE_DDL.ipynb`: seeds for `ctrl_cfg_schema_registry` and `ctrl_mng_pipeline_config` for the `slv_3p_*` targets
- Active tables: `lh_vv_silver.dbo.slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_rating`, `slv_3p_poi_amenity`, `slv_3p_poi_review`, `slv_3p_poi_media`. `slv_3p_poi_policy` is inactive.
- Consumers that read those columns: silver L2 `slv_poi_*`, and `gld_enr_*` in `notebooks/NB_ENR_POI_INFO.ipynb`, `notebooks/NB_ENR_POI_COORDINATE.ipynb`, and `notebooks/NB_ENR_POI_REVIEW.ipynb`. Name affected consumer tables and columns only. Do not redesign those consumers.
- Partner extract is out of scope.
- Sample file, outside the repository: `C:\Users\bachnh\Downloads\sample_3rd.txt`. Read that file only. Do not list or open anything else under Downloads. Do not copy the sample into the repository. Record keys and JSON types only. Do not record values, review text, person names, URIs, or URLs.

The user supplied a key tree on 2026-10-13 as a cross-check, not as a schema contract. Verify it against the sample file. If the file disagrees, follow the file and record the difference as a question, still without values.

User cross-check tree:

- `$` object
- `id`, `displayName`, `formattedAddress`, `businessStatus`, `primaryType`, `googleMapsUri`, `shortFormattedAddress` string
- `rating`, `userRatingCount`, `utcOffsetMinutes` number
- `priceLevel`, `currentOpeningHours`, `regularOpeningHours`, `internationalPhoneNumber`, `websiteUri`, `nationalPhoneNumber`, `accessibilityOptions`, `editorialSummary`, `generativeSummary`, `reviewSummary`, `priceRange`, `evChargeOptions`, `fuelOptions` null in the sample
- `location` object: `latitude`, `longitude` number
- `types` array of string
- `photos` array of object: `name`, `widthPx`, `heightPx`, `authorAttributions[]`, `flagContentUri`, `googleMapsUri`
- `addressComponents` array of object: `longText`, `shortText`, `types`, `languageCode`
- `primaryTypeDisplayName` object: `text`, `languageCode`
- `plusCode` object: `globalCode`, `compoundCode`
- `reviews` array of object: `name`, `relativePublishTimeDescription`, `rating`, `text`, `originalText`, `authorAttribution`, `publishTime`, `flagContentUri`, `googleMapsUri`
- `parkingOptions`, `paymentOptions`, `googleMapsLinks` object
- Boolean flags present in the sample include `servesCoffee`, `outdoorSeating`, `restroom`, `parkingOptions.freeStreetParking`, `paymentOptions.acceptsCashOnly`. Other `serves*` and `goodFor*` flags are present and null in the sample
- `routingSummaries`, `regularSecondaryOpeningHours`, `currentSecondaryOpeningHours` array
- `reservable`, `takeout`, `delivery`, `dineIn`, `curbsidePickup`, `pureServiceAreaBusiness` null in the sample

## Rules for the proposal

- One sample is not a schema contract. `currentOpeningHours` and `regularOpeningHours` being null in this sample does not mean every place is null.
- The extract only splits structure and casts types. Do not add business rules.
- Do not propose dropping bronze `normalized_payload` in this turn.
- Do not apply the mapping.
- Every current L1 column with no corresponding key in the sample has status `MISSING_EVIDENCE`. Do not write that the column is always null.
- `poi_id` remains `HASH_MD5_UUID` of `source_name` and `source_id` when both can still be determined from raw. If sample `id` is not sufficient to replace `source_id`, write a question. Do not invent a new formula.
- For each changed or removed column, name the consumer table and target column.
- Write `decision_md` in Vietnamese. Keep commands, identifiers, paths, status tokens, and column names in English.
- Write `payload_shape_md` in English. Keys and JSON types only.

## decision_md

Start `decision_md` with this text, unchanged, including the heading:

## Ngoại lệ model

Người dùng duyệt ngày 2026-10-13. Người viết đề xuất này là Claude Code, model `claude-opus-5-5`, effort `medium`. Đây không phải lượt Architect. Architect vẫn là `claude-opus-5-5` effort `high` và chỉ viết `architecture.md` qua `run-gate`. `models.architect.effort` giữ `high` vì validator từ chối giá trị khác.

Then write the proposal:

- One Markdown table for each `slv_3p_*` table. Each row is a column action: giữ, đổi `src_object` hoặc `json_path`, đổi kiểu, thêm cột, hoặc gỡ khỏi registry. Include `MISSING_EVIDENCE` where required.
- One Markdown table for `ctrl_cfg_schema_registry` and `ctrl_mng_pipeline_config`. Each row names the config row and which of `json_path`, `src_object`, `load_mode`, `data_type`, or `is_active` would change.
- A separate list of sample keys that have no current L1 column, each with a proposed target table or the exact phrase `chưa có chỗ chứa`.
- A section `Câu hỏi` containing every open question, including the `source_id` question when it applies.
- Do not add commentary that is not part of the proposal. Do not wrap the Markdown in fences inside the JSON string.

## payload_shape_md

A key tree of the sample object. For each node record the JSON type. Where a key is JSON null in this sample, record type `null` and that this is one sample only. Do not record values, review text, person names, URIs, or URLs. State that the tree is not a schema contract.

Return only the structured JSON object. Do not edit the workspace.
