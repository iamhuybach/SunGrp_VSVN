# Request

## User outcome

3 phần xử lý của 3 bảng sau đã out of date:
- gld_enr_poi_coordinate
- gld_enr_poi_info
- gld_enr_poi_review
Hãy cập nhật lại theo logic mới:
Với gld_enr_poi_coordinate: Bỏ
Với gld_enr_poi_review: Giữ nguyên
Với gld_enr_poi_info:
- Lấy toàn bộ các cột (trừ các cột op như row_hash, created_at, updated_at, deleted_at) của bảng slv_poi_entity_non_enrich thay cho slv_pn_poi.
- Bỏ các fields: subcategory_tags, short_address, best_time_from_month, best_time_to_month, best_time_type.
- district = slv_poi_entity_non_enrich.ward, destination_name = slv_poi_entity_non_enrich.city
- rating, userRatingCount (đổi thành user_rating_count), priceLevel (đổi thành price_level), opening_hours_text, review_json với slv_poi_entity_non_enrich.source_name = 'google' xử lý như cũ.
- left join slv_poi_amenity on slv_poi_entity_non_enrich.poi_id = slv_poi_amenity.poi_id để lấy slv_poi_amenity.service_flags
- lấy thêm 2 cột price_min và price_max khi join với slv_3p_poi_price -> tính cost theo mục 1.9.3 trong docs/context/3p-google/mapping_place_type.md
- time_to_spend, best_time, cost_vnd transform theo D:\git\SunGrp_VSVN\docs\context\3p-google\mapping_gld_enr_poi_info.md
- Các phần xử lý còn lại vẫn giữ nguyên.

## Cách hiểu đã chốt

- Schema gold là lh_vv_gold.enr. Nguồn info là lh_vv_silver.dbo.slv_poi_entity_non_enrich. Bỏ slv_pn_poi khỏi nguồn của ba bảng này.
- gld_enr_poi_coordinate: bỏ khỏi xử lý. Tắt cạnh ctrl tới bảng này. Notebook NB_ENR_POI_COORDINATE không còn được pipeline gọi. Không DROP bảng vì request không cho phép xóa bảng.
- gld_enr_poi_review: giữ nguyên logic NB_ENR_POI_REVIEW và hợp đồng cột.
- Cột op không đưa sang gold: row_hash, created_at, updated_at, deleted_at. Cột nghiệp vụ của entity, gồm website_url và các cột estimate, vẫn lấy.
- Bỏ khỏi gld_enr_poi_info: subcategory_tags, short_address, best_time_from_month, best_time_to_month, best_time_type. canonical_candidate chỉ đi vào best_time theo mục 1.2 của mapping_gld_enr_poi_info.md. Không tạo lại cột best_time_type.
- district lấy ward, destination_name lấy city của entity.
- Năm cột rating, user_rating_count, price_level, opening_hours_text, review_json chỉ áp rule google hiện có khi source_name = google. Đổi tên userRatingCount thành user_rating_count và priceLevel thành price_level.
- cost chỉ tính khi có đủ price_min và price_max, theo mục 1.9.3: ROUND((price_min + price_max) / 2), cost_method = observed_average, cost_confidence = high. Không gọi LLM. Thiếu một trong hai giá thì ghi USER_DECISION.
- time_to_spend, best_time, cost_vnd làm theo mục 1.1, 1.2, 1.3 và mục 2 của mapping_gld_enr_poi_info.md. cost null thì JSON null, không phải object có value null.
- Mục 1.3 mới chỉ có tiêu đề "round về 1,000 VND", chưa có công thức. Ghi USER_DECISION, không tự đặt cách làm tròn.
- Join amenity và join price không được nhân dòng gold. slv_poi_amenity có nhiều dòng cho một poi_id. Chưa có quy tắc gộp service_flags. Ghi USER_DECISION, không chọn mảng, concat hay một dòng.

## Scope

### In scope

- `notebooks/NB_ENR_POI_INFO.ipynb`: đổi nguồn và hợp đồng cột theo các quyết định đã chốt.
- Cạnh `ctrl_mng_pipeline_config` của `PL_VV_TRANS_SLV_TO_ENR_15P` trong `notebooks/NB_SETUP_INITIAL_DDL.ipynb` và một cell patch mới của `notebooks/NB_CREATE_DDL.ipynb`.
- Hợp đồng cột `lh_vv_gold.enr.gld_enr_poi_info` ở cả hai notebook DDL.
- `tests/test_enr_poi_contract.py` và phần gold enr của `tests/test_initial_ddl_contract.py` khi hợp đồng hoặc cạnh đổi.

### Out of scope

- Sửa logic hoặc hợp đồng cột `NB_ENR_POI_REVIEW`.
- DROP bảng `gld_enr_poi_coordinate` hoặc sửa logic `NB_ENR_POI_COORDINATE`.
- Sửa JSON `pipelines/PL_VV_TRANS_SLV_TO_ENR_15P` khi tắt cạnh ctrl đã đủ để orchestrator không gọi notebook coordinate.
- Gọi LLM để sinh cost.
- Tự đặt công thức làm tròn mục 1.3 hoặc quy tắc gộp `service_flags`.

## Acceptance criteria

- `gld_enr_poi_info` đọc `lh_vv_silver.dbo.slv_poi_entity_non_enrich` và không còn đọc `slv_pn_poi`.
- Ba cạnh ctrl tới `gld_enr_poi_coordinate` có `is_active = 0`. Bảng coordinate còn trong DDL. Pipeline không gọi `NB_ENR_POI_COORDINATE`.
- `gld_enr_poi_review` giữ nguyên logic và danh sách cột.
- Các USER_DECISION trong `decision.md` được người dùng chốt trước khi viết architecture.

## Constraints

- Không DROP bảng.
- Không nhân dòng gold khi join amenity hoặc price.
- Không bịa công thức làm tròn, quy tắc gộp `service_flags`, hoặc cách ghi cost khi thiếu `price_min` hoặc `price_max`.
- DDL: sửa định nghĩa tại chỗ trong `NB_SETUP_INITIAL_DDL`; `NB_CREATE_DDL` chỉ thêm cell patch mới. Cell `enrddlpy` giữ nguyên.

## Classification rationale

- Complexity: high. Đổi grain nguồn của gold info, đổi hợp đồng cột, tắt cạnh ctrl và giữ idempotency của seed. Signals: `data_model_change`, `cross_system`, `cross_state_impact`, `idempotency`, `design_tradeoffs`, `runtime_proof_required`.
- Risk: high. Đổi nguồn gold và tắt cạnh làm orchestrator bỏ một node trong khi bảng cũ vẫn còn; chạy lại trên DEV mới chứng minh được cạnh đã tắt.
- Architecture: required. Đổi nguồn gold, tắt cạnh coordinate, đổi hợp đồng cột info. Không fast lane.
- Evidence: not required ở triage. Grain `slv_poi_amenity` đã có trong `docs/context/01_DATA_MODEL.md` §6. `slv_3p_poi_price` là DOC khóa `poi_id`. Ba điểm chặn là quyết định nghiệp vụ, không phải probe.
- Runtime proof: required. Sau review, runbook chạy lại `gld_enr_poi_info` trên Fabric DEV và kiểm tra cạnh coordinate đã tắt. `p_apply` mặc định false.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, rồi `risk-gate`. Không thêm `fabric-pipeline-reviewer`: pipeline JSON chỉ gọi orchestrator `NB_00_ORCHES_SLV_TO_ENR_15P`; việc tắt node nằm ở cạnh ctrl.
