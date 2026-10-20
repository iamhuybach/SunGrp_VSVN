# Request

## User outcome

Bảng slv_poi_entity_non_enrich đang thừa những cột _crawled_at, _event_id, _first_seen_at, _last_seen_at. Đây là cột op của nguồn 3rd, không lấy vào bảng này.
Thêm cột website_url với 3p (google) lấy từ slv_3p_poi_contact.website_url và partner lấy từ slv_pn_business_services.website_urls (lấy đường dẫn trong key website_url; data sample {"website_url":"https://stg-partner-portal-internal.visitvietnam.asia/"}).
Hãy sửa lại, có thể drop bảng, delete watermark để chạy lại như một lần init vì đây là môi trường dev.

Yêu cầu bổ sung:

- Thêm những cột sau cho bảng slv_poi_entity_non_enrich:
  - range_low_min = ref_dictionary_place_type.range_low_min
  - range_high_min = ref_dictionary_place_type.range_high_min
  - avg_range_min = ref_dictionary_place_type.avg_range_min
  - candidate_best_time_code = ref_dictionary_place_type.candidate_best_time_code
  - canonical_candidate = ref_dictionary_place_type.canonical_candidate
- Thêm cột service_flags = ref_dictionary_amenities.service_flags cho bảng slv_poi_amenity.
- Vẫn có thể drop bảng, delete watermark để chạy lại như một lần init vì đây là môi trường dev.

## Scope

### In scope

- Remove `_crawled_at`, `_event_id`, `_first_seen_at`, and `_last_seen_at` from `lh_vv_silver.dbo.slv_poi_entity_non_enrich` only.
- Add nullable STRING `website_url` on that table: google from `slv_3p_poi_contact.website_url` by `poi_id`; partner from JSON key `website_url` in `slv_pn_business_services.website_urls`.
- Copy `range_low_min`, `range_high_min`, `avg_range_min`, `candidate_best_time_code`, and `canonical_candidate` onto `slv_poi_entity_non_enrich` from the `ref_dictionary_place_type` row the entity already matched. No second match rule.
- Copy `service_flags` onto `slv_poi_amenity` from the `ref_dictionary_amenities` row the amenity already matched. Do not reseed either dictionary.
- DEV drop and watermark delete only for `slv_poi_entity_non_enrich` and `slv_poi_amenity`, then rerun as init. User runs Fabric DEV.

### Out of scope

- The four op columns on `slv_3p_*`.
- Dropping source tables, `ref_dictionary_place_type`, or `ref_dictionary_amenities`.
- Reseeding either dictionary.
- Writing the sample URL into a seed or a test.
- Marking `gates.runtime`.

## Acceptance criteria

- `slv_poi_entity_non_enrich` no longer has the four op columns and has nullable STRING `website_url`.
- Google rows take `slv_3p_poi_contact.website_url` through `poi_id`. Partner rows take the `website_url` key inside `website_urls`; a missing key is null.
- `slv_3p_*` still has the four op columns.
- `slv_poi_entity_non_enrich` also has the five estimate columns from the dictionary row it already matched.
- `slv_poi_amenity` has `service_flags` from the dictionary row it already matched.
- A DEV runbook drops only `slv_poi_entity_non_enrich` and `slv_poi_amenity`, deletes only those tables' watermarks, and reruns as init. `p_apply` defaults to false. The apply step is separate.

## Constraints

- Schema is `lh_vv_silver.dbo`. Contact grain in the data model is `poi_id`. If more than one contact row exists for one `poi_id`, record `USER_DECISION` and do not pick a row.
- Do not write the sample URL into a seed or a test.
- The five estimate columns come from the `ref_dictionary_place_type` row the entity already matched. Do not add a second match rule.
- `service_flags` comes from the `ref_dictionary_amenities` row `slv_poi_amenity` already matched. Do not reseed either dictionary.
- Drop and delete watermarks only for `slv_poi_entity_non_enrich` and `slv_poi_amenity` on DEV. Do not drop `ref_dictionary_place_type` or `ref_dictionary_amenities`.
- The runbook names DEV, a count before delete, the drop statement, which watermark rows are deleted, how to rebuild, and how to roll back. The user runs Fabric DEV. The agent does not set `gates.runtime`.

## Classification rationale

- Complexity: high. Column removal and a new column change the silver L2 grain projection, the node input set, and the pipeline edges that amenity setup counts.
- Risk: high. The change alters silver columns and edge watermarks. DEV recovery is drop-and-reinit of one table.
- Architecture: required. A silver column change and a watermark change are not a fast lane.
- Evidence: not required at triage. Contact grain is `poi_id` in `docs/context/01_DATA_MODEL.md` and the registry key is `poi_id`. A duplicate `poi_id` in contact is a `USER_DECISION`, not a row-picking rule. Probe only if the architecture gate returns `EVIDENCE_REQUIRED`.
- Runtime proof: required. The user runs the DEV drop, watermark delete, and init rerun. `gates.runtime` stays pending.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, and `risk-gate` (risk high).
