# Request

## User outcome

Chuyển `slv_poi_amenity` và `slv_poi_entity_non_enrich` từ `PL_VV_TRANS_SLV_TO_SLV_1H` sang `PL_VV_TRANS_SLV_TO_ENR_15P`, vì hai bảng này là đầu vào của các bảng đích trong luồng 15 phút.

Làm sạch môi trường: xóa bảng và cấu hình không còn dùng.

- Bảng: `gld_enr_poi_coordinate`, `slv_pn_poi`.
- Luồng `gld_enr_poi_info` cũ, chạy bằng `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi`.
- Luồng `slv_pn_poi`.

## Cách hiểu đang dùng

Chưa phải quyết định đã chốt. Sửa lại nếu khác ý.

- Chuyển mọi cạnh `ctrl_mng_pipeline_config` có `trg_tbl` là `slv_poi_amenity` hoặc `slv_poi_entity_non_enrich` từ `PL_VV_TRANS_SLV_TO_SLV_1H` sang `PL_VV_TRANS_SLV_TO_ENR_15P`. Mỗi node chỉ thuộc một pipeline active. Seed hiện có 6 cạnh vào entity và 3 cạnh vào amenity, gồm cạnh `slv_3p_poi_contact` → `slv_poi_entity_non_enrich`.
- `PL_VV_TRANS_SLV_TO_ENR_15P` chỉ gọi `NB_00_ORCHES_SLV_TO_ENR_15P`. Thứ tự node lấy từ cạnh ctrl. Hai node silver phải chạy trong cùng DAG với `gld_enr_poi_info`.
- Không đổi pipeline JSON. Không có file pipeline cho `PL_VV_TRANS_SLV_TO_SLV_1H`.
- Xóa cấu hình nghĩa là xóa dòng ctrl, không chỉ đặt `is_active = 0`.
- Luồng info cũ là 3 cạnh đã tắt: `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact` → `gld_enr_poi_info`. Không DROP ba bảng silver L1 đó. Không tắt các cạnh info đang active (`slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `slv_pn_business_service_i18ns`).
- Luồng `slv_pn_poi` là 2 cạnh active trên `PL_VV_TRANS_SLV_TO_ENR_15P`: `slv_pn_business_services` và `slv_pn_business_service_i18ns` → `slv_pn_poi`, notebook `NB_SLV_PN_POI`.
- Luồng coordinate là 3 cạnh đã tắt tới `gld_enr_poi_coordinate`, notebook `NB_ENR_POI_COORDINATE`.
- DROP `lh_vv_gold.enr.gld_enr_poi_coordinate` và `lh_vv_silver.dbo.slv_pn_poi` trên Fabric DEV. Gỡ DDL, seed, notebook và test tương ứng trong repo.
- Watermark cạnh `wm_e__<trg>__<src>` và khoá `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` nằm trong phạm vi dọn nếu probe thấy chúng. Không xóa `ctrl_log_run` hay `ctrl_log_table_run`.
- Không đụng `gld_enr_poi_review`, `slv_poi_entity`, hay các cạnh extract `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`.
- Sau khi chuyển, seed không còn cạnh `PL_VV_TRANS_SLV_TO_SLV_1H`.

## Scope

### In scope

- Cạnh ctrl và seed của hai node `slv_poi_amenity`, `slv_poi_entity_non_enrich`.
- Xóa cạnh và notebook của `slv_pn_poi` và `gld_enr_poi_coordinate`.
- DROP hai bảng đó trên Fabric DEV, có rollback trong runbook.
- `NB_SETUP_INITIAL_DDL` sửa định nghĩa tại chỗ. `NB_CREATE_DDL` chỉ thêm cell patch mới.
- `NB_SETUP_POI_ENTITY`, `NB_SETUP_POI_AMENITY`, và test contract đang khóa tên pipeline hoặc hai bảng bị xóa.
- Đoạn mô tả pipeline trong `docs/context/CTRL_TABLES_CONTEXT.md` và `docs/context/01_DATA_MODEL.md` cho đúng seed mới.

### Out of scope

- Logic build của `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_SLV_POI_AMENITY`, `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`.
- DROP `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_poi_entity`.
- Xóa log lịch sử.
- Commit, merge, hoặc chạy notebook trên Fabric. Người dùng chạy probe và runbook.

## Acceptance criteria

- Mọi cạnh active của `slv_poi_amenity` và `slv_poi_entity_non_enrich` có `pl_name = PL_VV_TRANS_SLV_TO_ENR_15P`. Không còn cạnh active nào của hai bảng này trên `PL_VV_TRANS_SLV_TO_SLV_1H`.
- `NB_00_ORCHES_SLV_TO_ENR_15P` xếp `slv_poi_entity_non_enrich` trước `slv_poi_amenity`, và cả hai trước `gld_enr_poi_info`.
- Không còn dòng ctrl tới `slv_pn_poi` hoặc `gld_enr_poi_coordinate`.
- Không còn 3 cạnh info cũ từ `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`.
- Trên Fabric DEV, hai bảng `gld_enr_poi_coordinate` và `slv_pn_poi` không còn. `gld_enr_poi_info` và `gld_enr_poi_review` còn.
- Chạy lại cell patch không tạo lại cạnh đã xóa và không nhân đôi cạnh đã chuyển.
- Repo không còn `NB_SLV_PN_POI` và `NB_ENR_POI_COORDINATE`.

## Constraints

- Chỉ Fabric DEV. Không đụng staging hay production.
- Không bịa dòng ctrl hoặc watermark còn sống ngoài probe.
- `NB_CREATE_DDL`: thêm cell patch, không viết lại cell lịch sử.
- Một node không được có cạnh active ở hai pipeline.
- Probe và runbook do người dùng chạy. Agent không ghi nhận là đã chạy Fabric.

## Classification rationale

- Complexity: high. Đổi pipeline của node có cạnh, watermark và notebook setup; đồng thời DROP bảng và xóa cấu hình.
- Risk: high. Xóa bảng và đổi DAG ctrl có thể làm lệch watermark hoặc thứ tự chạy. Rollback bằng Delta time travel và seed đã biết, nên không xếp critical.
- Architecture: required. Đổi cấu trúc orchestration, chủ sở hữu trạng thái ctrl, và ranh giới commit giữa patch config và DROP.
- Evidence: required. Tập cạnh và watermark đang sống trên DEV quyết định patch xóa gì. Seed trong repo không chứa mọi dòng đã retire trên DEV.
- Runtime proof: required. Phải thấy DAG 15 phút chạy đúng thứ tự và hai bảng đã DROP.
- Reviewer routing: `fabric-pipeline-reviewer`, `state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer`, rồi `risk-gate`.
- `data_model_change`: sau evidence, `model-design.md` phải có trước Architect.
