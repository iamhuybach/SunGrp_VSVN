# Request

## User outcome

Partner opening hours with two intervals in one day are written, and silver plus gold media use the grain `media_id` + `poi_id`. User 2026-11-05, verbatim:

- Với những block có 2 mảng hours, vẫn phải xử lý cả 2.
- Với bảng slv_poi_media_info, grain/key sẽ gồm media_id và poi_id. Ở phần DataFrame nguồn sẽ xử lý merge trước, grain/key sẽ gồm media_id và poi_id và lấy theo updated_at lớn nhất.
- Khi nhiều dòng cùng media_id, cùng poi_id và cùng updated_at => Chọn dòng bất kỳ.
- Gallery đổi thành media_id + poi_id như silver.

The Monday record that produced `PARTNER_MULTI_HOURS` has `policies.operating_hours.monday.hours` of length 2: `08:00`–`09:00` and `11:00`–`22:00`. The other six days in that record have one element. Both Monday intervals must appear in the partner `operating_hours` output. The node must not raise `PARTNER_MULTI_HOURS` for that shape.

`slv_poi_media_info` and `gld_srv_poi_media_gallery` MERGE on `media_id` and `poi_id`. Before that MERGE, the media source DataFrame is reduced to one row per `media_id`, `poi_id`, keeping the greatest `updated_at`. Equal `updated_at` may keep any of the tied rows. A rerun with the same input must keep the same row.

## Scope

### In scope

- Partner hours transform in `NB_GLD_SRV_POI_INFO` and `docs/context/mapping_gld_srv_poi_info.md` §1.5.
- `NB_SLV_POI_MEDIA_INFO` source reduction and MERGE key.
- `NB_GLD_SRV_POI_MEDIA_GALLERY` MERGE key.
- `docs/context/mapping_poi_media_info.md`.
- Contract tests that currently require `PARTNER_MULTI_HOURS` or `pk == ("media_id",)`.

### Out of scope

- `NB_SLV_POI_ENTITY_NON_ENRICH`, review notebooks, enrich notebooks, and the orchestrator.
- PostgreSQL `sql/postgres/gld_srv_serve.pg.sql`.
- Changing the partner `media_id` hash or the Google `media_dedup_key` assignment.
- A day whose `hours` array has a length other than 2. Length 0 and length 1 stay on the current §1.5 rules. Length greater than 2 is not decided here.

## Acceptance criteria

- A partner day with exactly two `hours` elements emits both intervals and does not raise `PARTNER_MULTI_HOURS`.
- `NB_SLV_POI_MEDIA_INFO` and `NB_GLD_SRV_POI_MEDIA_GALLERY` use `pk` `("media_id", "poi_id")`.
- The media build output contains one row per `media_id`, `poi_id` before `quality_gate`.
- The kept row is one of the rows with the greatest source `updated_at`. The choice is stable across reruns.
- Mapping text matches the notebooks.

## Constraints

- Source `updated_at` is the technical column written by extract, not `src_updated_at` and not `last_updated_at`. Partner CDC tables and the 3p snapshot table both carry that column (`NB_LIB_EXTRACT_RAWDATA` `TECH_COLUMNS` and `SNAPSHOT_TECH_COLUMNS`). The media build must carry it onto each exploded element from its parent row.
- Three exploded elements from one i18n row share that parent's `updated_at`. The tie rule applies.
- Do not invent columns. The single-interval partner object shape in mapping §1.5 stays. Two intervals are two of those objects.
- Idempotency: "chọn dòng bất kỳ" allows any tied business row, and forbids a pick that changes between reruns.
- Task `20261104-poi-review-src-and-partner-i18n` already used review round 2. Do not edit its notebooks for this change.

## Classification rationale

- Complexity: high. Hours output shape and a MERGE grain change across silver and gold.
- Risk: high. MERGE key, source collapse, and rerun stability.
- Architecture: required. The grain and the commit key change.
- Evidence: not required. The eight hour keys and two media keys are in the parent task results. Column `updated_at` is in the extract contract.
- Runtime proof: not required. The hours function and the collapse are locally testable.
- Reviewer routing: `sql-data-reviewer`, `state-correctness-reviewer`, `spark-runtime-reviewer`.
