# 0. Hiện trạng `lh_vv_silver.dbo.slv_poi_amenity`

Mô tả lấy từ code hiện tại. Không thêm rule. Chỗ code không ghi: `MISSING`.

Nguồn: `notebooks/NB_SLV_POI_AMENITY.ipynb` (markdown đầu, `OUT_COLS`, `build`, `SPEC`), `notebooks/NB_SETUP_POI_AMENITY.ipynb` (DDL và ba cạnh), `tests/test_poi_amenity_contract.py` (`test_amenity_ddl_matches_node`, `test_amenity_node_contract`, `test_setup_contract`). `NB_CREATE_DDL` kiểm tra cùng ba cạnh active, `load_mode = RECOMPUTE`, trong `NODE_EDGES`.

- Bảng vật lý: `lh_vv_silver.dbo.slv_poi_amenity`. Notebook: `NB_SLV_POI_AMENITY`. `SPEC.trg_tbl = slv_poi_amenity`. `write_mode = MERGE`.
- Grain / khóa MERGE: (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`).
- `poi_id` trong `build` lấy từ bảng nguồn. Công thức hash của `poi_id` trong notebook này: `MISSING`.
- Pipeline của bảng này: `PL_VV_TRANS_SLV_TO_ENR_15P`. `load_mode = RECOMPUTE`, `priority = 1`, `is_active = 1`. Đây là pipeline hiện hữu của `slv_poi_amenity`, không gán cho bảng mới.
- Ba cạnh active, `src_schema` và `trg_schema` đều `lh_vv_silver.dbo`:
  1. `slv_3p_poi_amenity`
  2. `slv_poi_entity_non_enrich`
  3. `ref_dictionary_amenities`
- Cạnh `slv_poi_entity` → `slv_poi_amenity`: `RETIRE`, `is_active = 0`.
- `nb_name` trên cạnh: `NB_SETUP_POI_AMENITY` ghi `NULL` khi cột tồn tại.
- `SPEC.inputs`: `amenity` = `slv_3p_poi_amenity`, `entity` = `slv_poi_entity_non_enrich`, `dict` = `ref_dictionary_amenities`. `required_inputs` là cả ba.
- Cột nghiệp vụ `OUT_COLS`: `poi_id`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`, `amenity_vi`, `service_flags`.
- DDL: bốn cột khóa `STRING NOT NULL`. `amenity`, `amenity_vi`, `service_flags` là `STRING` nullable. Cột kỹ thuật nullable: `row_hash STRING`, `created_at TIMESTAMP`, `updated_at TIMESTAMP`, `deleted_at TIMESTAMP`.
- Markdown đầu: RECOMPUTE. Key cờ google khớp `source_flags_json` = true. Key tách từ `types[] =` khớp đúng một phần tử `types_json`. `json_type = 'a'` và `json_type in (...)` khớp một phần tử trong danh sách, cùng `types_json` của `slv_poi_entity_non_enrich`. `business_sector` từ `slv_poi_entity_non_enrich`.
- `build`: từ điển `source_name` google và `is_active = true`. `service_flags` lấy từ dòng điều kiện đã khớp. Không có `business_category`. DataFrame rỗng khi không khớp là trạng thái hợp lệ để RECOMPUTE soft-delete. Test cấm `explode_outer` và `get_json_object`.

# 1. Table: `gld_srv_poi_amenity`

Transform 1-1 từ `lh_vv_silver.dbo.slv_poi_amenity`, chỉ thay đổi `created_at` và `updated_at`. Không thêm cột nghiệp vụ ngoài `OUT_COLS`. Timestamp là field hệ thống của gold. Logic, grain, khóa và cạnh ctrl của `slv_poi_amenity` giữ nguyên.
