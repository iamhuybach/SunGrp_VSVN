# Request

## User outcome

Bảng gld_srv_poi_info xử lý thêm nghiệp vụ sau:
Với source = partner, nếu poi_id chưa có trong slv_enr_poi_destination, lấy trực tiếp từ slv_poi_entity_non_enrich. Field nào mà slv_poi_entity_non_enrich không có thì để null.
Lý do nghiệp vụ: POI partner chưa có dòng destination vẫn ra gold. Cột nào entity có thì lấy từ entity. Cột nào entity không có thì null.

## Scope

### In scope

- source = partner nghĩa là lower(trim(source_name)) = 'partner', cùng cách notebook đang so khớp. Không thêm cột source.
- Chưa có trong slv_enr_poi_destination nghĩa là không có dòng cùng poi_id. Dòng destination tồn tại nhưng cột null không thuộc nhánh này.
- Nhánh đó: cột gold đang lấy từ destination, entity có cột cùng tên thì lấy 1-1 từ slv_poi_entity_non_enrich. Entity không có cột đó thì null. Không lấy từ bảng khác, không coalesce với destination.
- Partner đã có dòng destination: giữ mapping hiện tại, cột destination vẫn 1-1 từ slv_enr_poi_destination.
- Cùng task cập nhật docs/context/mapping_gld_srv_poi_info.md trước review. Chỗ notebook không ghi thì MISSING.
- Danh sách cột entity có hay không lấy từ OUT_COLS của NB_SLV_POI_ENTITY_NON_ENRICH. Không chốt danh sách đó trong request.

### Out of scope

- Google, nguồn khác, operating_hours, holiday_exceptions, is_verified, is_recommended, is_bookable, rating_overall, rating_count, review_count: không đổi.
- Không thêm cột, không đổi grain poi_id, không thêm input.
- Không signal data_model_change chỉ vì đổi nguồn điền cột đã có. Architecture chỉ khi §Classification bắt buộc.
- Không đọc task khác, notebooks_lgc/, manifest pipeline.

## Acceptance criteria

- source = partner nghĩa là lower(trim(source_name)) = 'partner', cùng cách notebook đang so khớp. Không thêm cột source.
- Chưa có trong slv_enr_poi_destination nghĩa là không có dòng cùng poi_id. Dòng destination tồn tại nhưng cột null không thuộc nhánh này.
- Nhánh đó: cột gold đang lấy từ destination, entity có cột cùng tên thì lấy 1-1 từ slv_poi_entity_non_enrich. Entity không có cột đó thì null. Không lấy từ bảng khác, không coalesce với destination.
- Partner đã có dòng destination: giữ mapping hiện tại, cột destination vẫn 1-1 từ slv_enr_poi_destination.
- Google, nguồn khác, operating_hours, holiday_exceptions, is_verified, is_recommended, is_bookable, rating_overall, rating_count, review_count: không đổi.
- Không thêm cột, không đổi grain poi_id, không thêm input.
- Cùng task cập nhật docs/context/mapping_gld_srv_poi_info.md trước review. Chỗ notebook không ghi thì MISSING.

## Constraints

- Miền: lib transform/gold.
- Không signal data_model_change chỉ vì đổi nguồn điền cột đã có. Architecture chỉ khi §Classification bắt buộc.
- Danh sách cột entity có hay không lấy từ OUT_COLS của NB_SLV_POI_ENTITY_NON_ENRICH. Không chốt danh sách đó trong request.
- Không đọc task khác, notebooks_lgc/, manifest pipeline.

## Classification rationale

- Complexity: low. No complexity signal applies. One conditional projection in `NB_GLD_SRV_POI_INFO`.
- Risk: medium. Bounded behavior change for partner rows that have no destination row. Rollback is the notebook cell. Local contract tests cover the column split. Not fast lane: behavior changes and three source files change.
- Architecture: not required. Grain, key, state owner, transaction boundary, and commit order stay `poi_id` MERGE. Entity and destination are already inputs. No CDC, watermark, lock, retry, partial-failure, or pipeline-structure change. The acceptance criteria fix one implementation. The change is one notebook, one test, and one mapping file. `data_model_change` is not set: no table, column, grain, or key change.
- Evidence: not required. Column membership is `OUT_COLS` in `NB_SLV_POI_ENTITY_NON_ENRICH`. Overlapping address columns are STRING or DOUBLE on both `slv_poi_entity_non_enrich` (`NB_SETUP_INITIAL_DDL` cell `init_tables`) and the destination columns already projected to gold (`NB_CREATE_DDL` cell `srvpoipy`). Row absence is the existing `_destination` key, not a data-distribution question.
- Runtime proof: not required.
- Reviewer routing: `spark-runtime-reviewer` (PySpark notebook build and Delta MERGE write) and `sql-data-reviewer` (join and projection that feed `write_mode=MERGE`). Not `state-correctness-reviewer` (commit order, watermark, locks, and retry stay). Not `fabric-pipeline-reviewer` (no pipeline change). Risk is medium, so no risk gate.
