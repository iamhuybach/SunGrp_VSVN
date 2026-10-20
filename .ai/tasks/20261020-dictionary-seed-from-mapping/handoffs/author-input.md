# Author input model

No `proposal.md`. Accepted scope is `decision.md` `Quyết định hiện hành` D-01 through D-05 and `request.md` Constraints.

Read:

- `.ai/tasks/20261020-dictionary-seed-from-mapping/decision.md` section `Quyết định hiện hành`
- `.ai/tasks/20261020-dictionary-seed-from-mapping/request.md` section Constraints
- `docs/context/3p-google/mapping_place_type.md` L184-L270
- `docs/context/3p-google/mapping_amenities.md` L142-L155
- `docs/context/01_DATA_MODEL.md` L343-L344
- `docs/context/02_NAMING_CONVENTION.md` L39-L64

Tables: `lh_vv_silver.dbo.ref_dictionary_place_type`, `lh_vv_silver.dbo.ref_dictionary_amenities`.

Do not invent `OUTDOOR_TYPES` members, `source_name`, or amenity tokens outside D-05.
`suối` and `thác` stay as written. Section 1.9.3 is not a seed column.
Column labels are the markdown headers `default_range(min)`, `avg_range(min)`, `candidate_best_time_code`, and `canonical_candidate`.
