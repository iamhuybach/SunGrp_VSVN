# Author input — model

User comments, verbatim:

- Thêm những cột sau cho bảng slv_poi_entity_non_enrich:
  - range_low_min = ref_dictionary_place_type.range_low_min
  - range_high_min = ref_dictionary_place_type.range_high_min
  - avg_range_min = ref_dictionary_place_type.avg_range_min
  - candidate_best_time_code = ref_dictionary_place_type.candidate_best_time_code
  - canonical_candidate = ref_dictionary_place_type.canonical_candidate
- Thêm cột service_flags = ref_dictionary_amenities.service_flags cho bảng slv_poi_amenity.
- Vẫn có thể drop bảng, delete watermark để chạy lại như một lần init vì đây là môi trường dev.
- Năm cột estimate lấy từ dòng ref_dictionary_place_type mà entity đã khớp. Không thêm rule khớp thứ hai.
- service_flags lấy từ dòng ref_dictionary_amenities mà slv_poi_amenity đã khớp. Không seed lại hai bảng từ điển.
- Drop và xóa watermark chỉ với slv_poi_entity_non_enrich và slv_poi_amenity trên DEV. Không drop ref_dictionary_place_type hay ref_dictionary_amenities.

Keep D1–D8: drop four op columns from the entity only; add nullable STRING website_url (google left join on poi_id; partner top-level $.website_url). Do not design drop or watermarks.

Ledger rows to implement: D1, D2, D9, D10. No proposal.md.

Read:

- `decision.md` `Quyết định hiện hành`
- `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` cell `b1entitybuild` (`CATEGORY_COLS`, `pick`, partner select)
- `notebooks/NB_SLV_POI_AMENITY.ipynb` cell `d1amenbuild` (`OUT_COLS`, dict collect, joins)
- `notebooks/NB_SETUP_POI_ENTITY.ipynb` cell `a1setupddl` types of the five estimate columns
- `notebooks/NB_SETUP_POI_AMENITY.ipynb` cell DDL type of `service_flags`

Constraints: copy types from those DDL cells. Do not invent a second match. If google and partner already select different dictionary rows, ask; do not choose. Do not copy sample URLs. Do not reseed.
