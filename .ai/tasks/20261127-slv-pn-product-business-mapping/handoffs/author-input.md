# Author input — model

No `proposal.md`. Do not re-analyze the business. Do not propose another layer. `problem-analysis.md` is historical. Q-01 through Q-19 and the two mappings supersede it.

Verbatim user outcome: Hiện thực đúng hai mapping đã chốt. Không phân tích lại nghiệp vụ. Không đề xuất lại lớp.

## Read only

- `docs/context/mapping_slv_pn_product.md` — intro, `## Quyết định đã chốt`, `## Câu hỏi cần chốt`, and each `### Xử lý` / `### Field Mapping`. L1 contract is unchanged.
- `docs/context/mapping_slv_pn_product_l2.md` — `## 1` through `## 3`, including `### 1.3. Giải mã giá` and `### 3.3. meal_plan`.
- `.ai/tasks/20261127-slv-pn-product-business-mapping/decision.md` — `## Quyết định hiện hành`, Q-01 through Q-19.
- `.ai/tasks/20261127-slv-pn-product-business-mapping/evidence/results/product_payload_shape.txt` — cited types only.
- `docs/context/02_NAMING_CONVENTION.md` — §1 silver prefix rows and the Silver L2 technical-column row.
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` — `TABLE_CONFIGS` of the 13 `slv_pn_product*` and `slv_pn_hotel*` tables, read-only (Q-01). `TABLE_SPECS` only to confirm the three L2 tables are absent.
- `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` — `TECH_COLUMNS`, only to separate L1 extract columns from L2 technical columns.
- `notebooks_lgc/pl_transform_partner_userprofile_cms/5. nb_prepare_product_for_ingestion.ipynb` — cell 15 only, for the `valid_from` / `valid_to` sentence in mapping L2 `### 3.1`.

## Constraints

- New tables and grain, Q-19 and mapping L2: `slv_pn_product_sale` (`product_id`), `slv_pn_hotel_room_offer` (`room_type_id`), `slv_pn_hotel_rate_offer` (`rate_plan_id`). Lakehouse `lh_vv_silver.dbo`.
- `valid_from` and `valid_to` on `slv_pn_hotel_rate_offer` are 1-1. NULL stays NULL. No sale flag from those columns. Cell 15 only casts them to string for `variants_json`.
- Price NULL stays NULL (Q-15). Do not write 0. L1 keeps price strings (Q-03). L2 decode is only mapping L2 `### 1.3`.
- No `variants_json`, no LLM, no destination remap, no `source_id`, no destination on L1 or L2, no `poi_id` on the three L2 tables.
- Do not add a column, grain, or key to the 13 L1 tables. The four items under mapping L1 `## Câu hỏi cần chốt` stay open. Do not invent a column to close them.
- A rule absent from the settled mapping or from cell 15 goes under `## Conflicts and questions`. Do not invent the column, type, or key.
- Q-19 names stand. If §1 `slv_poi_<chủ đề>` disagrees, record that conflict as closed by Q-19. Do not rename.
- L2 technical columns are the mapping L2 intro and the Silver L2 naming row: `row_hash`, `created_at`, `updated_at`, `deleted_at`. L2 `deleted_at` is the recompute soft-delete, not the L1 source `deleted_at` (Q-16).
- Q-11 clauses "2 bảng mới" and "Tài liệu L2 chưa tạo" are stale. Q-19 wins. The L2 mapping file exists.
