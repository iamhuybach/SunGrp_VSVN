# Author input — model

User 2026-11-05, verbatim:

- Với những block có 2 mảng hours, vẫn phải xử lý cả 2.
- Với bảng slv_poi_media_info, grain/key sẽ gồm media_id và poi_id. Ở phần DataFrame nguồn sẽ xử lý merge trước, grain/key sẽ gồm media_id và poi_id và lấy theo updated_at lớn nhất.
- Khi nhiều dòng cùng media_id, cùng poi_id và cùng updated_at => Chọn dòng bất kỳ.
- Gallery đổi thành media_id + poi_id như silver.

Read:

- docs/context/mapping_gld_srv_poi_info.md §1.5
- notebooks/NB_GLD_SRV_POI_INFO.ipynb cell id srvinfohours, def partner_hours
- docs/context/mapping_poi_media_info.md §1 and §2
- notebooks/NB_SLV_POI_MEDIA_INFO.ipynb cell id slvmediabuild
- notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb NodeSpec
- docs/context/NB_LIB_EXTRACT_RAWDATA.md TECH_COLUMNS and SNAPSHOT_TECH_COLUMNS

Constraints:

- Monday example: hours length 2 is 08:00–09:00 and 11:00–22:00. Emit both. Do not raise PARTNER_MULTI_HOURS for length 2.
- Length 0 and 1 stay on §1.5. Length greater than 2 is out of scope.
- Keep the existing single-interval partner object shape. Two intervals are two of those objects.
- pk of both media tables is (media_id, poi_id).
- Collapse the source DataFrame before quality_gate. Rank by parent technical column updated_at, not src_updated_at and not last_updated_at.
- Copy that parent updated_at onto each exploded element. Elements from one parent share it.
- Equal updated_at may keep any tied row. The kept row must be the same on every rerun. Name the total order using columns the build already has.
- Do not change the media_id formulas. Do not add columns.

Parent evidence, do not copy the files:

- .ai/tasks/20261104-poi-review-src-and-partner-i18n/evidence/results/partner_multi_hours.txt
- .ai/tasks/20261104-poi-review-src-and-partner-i18n/evidence/results/media_pk_duplicate.txt
