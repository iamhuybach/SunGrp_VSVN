# Request

## User outcome

Xử lý 3 bảng `slv.slv_poi_media_info`, `gld_srv_poi_media_gallery` và `gld_srv_poi_amenity` theo 2 file mapping sau:

- `docs/context/mapping_poi_media_info.md`
- `docs/context/mapping_gld_srv_poi_amenity.md`

Ngoài ra, bổ sung nghiệp vụ và mapping hiện tại của `slv.slv_poi_amenity` vào `docs/context/mapping_gld_srv_poi_amenity.md`.

Đọc mapping thế này:

- `slv.` là nhãn tầng silver, bảng vật lý `lh_vv_silver.dbo`. `gld_srv_*` là `lh_vv_gold.dbo`. Không tạo schema SQL tên `slv`.
- `slv_poi_media_info` là bảng silver mới. Nguồn là union `slv_3p_poi_media` với nhánh partner trong §1.1. Chữ "Append" trong mapping là gộp nguồn, không phải Delta append-only.
- `gld_srv_poi_media_gallery` là gold mới, transform 1-1 từ `slv_poi_media_info`, chỉ khác `created_at` và `updated_at`.
- `gld_srv_poi_amenity` là gold mới, transform 1-1 từ `lh_vv_silver.dbo.slv_poi_amenity`, chỉ khác `created_at` và `updated_at`.
- Không đổi logic, grain, khóa hay cạnh ctrl của `slv_poi_amenity`. Chỉ mô tả hiện trạng của bảng đó vào `mapping_gld_srv_poi_amenity.md`, rồi mới ghi rule gold 1-1.

Một task cho đủ ba bảng. Không tách media và amenity.

## Scope

### In scope

- DDL, registry, cạnh ctrl và node notebook `NB_<UPPER(trg_tbl)>` cho `slv_poi_media_info`, `gld_srv_poi_media_gallery`, `gld_srv_poi_amenity`.
- `NB_CREATE_DDL` và `NB_SETUP_INITIAL_DDL` cùng một bộ bảng và cạnh.
- Test contract của ba bảng đích.
- Mô tả hiện trạng `slv_poi_amenity` trong `docs/context/mapping_gld_srv_poi_amenity.md`, lấy từ notebook, DDL và test. Thiếu trong code thì ghi `MISSING`.
- Miền: lib transform/gold và DDL/registry.

### Out of scope

- Đổi logic, grain, khóa hoặc cạnh ctrl của `slv_poi_amenity`.
- Sửa notebook trước khi architecture `PASS`.
- Gán `pl_name` từ mẫu `gld_srv_poi_info` hoặc từ chỗ mapping không ghi.
- Tách task media và task amenity.
- Fast lane.
- Đọc `docs/context/3p-google/*.txt`. Chỉ mở `docs/context/3p-google/poi_amenity_mapping.md` khi notebook amenity trích đúng file đó.

## Acceptance criteria

- Ba bảng đích có DDL, registry, node notebook `NB_<UPPER(trg_tbl)>`, cạnh ctrl không nhân đôi, và test contract.
- `NB_CREATE_DDL` và `NB_SETUP_INITIAL_DDL` cùng một bộ bảng và cạnh.
- Media partner: `locale = vi`; `media` của i18n null hoặc rỗng thì lấy `slv_pn_business_services.media` cùng `poi_id`. `poi_id` partner giữ công thức đã có `uuid_md5(id, 'partner')`.
- Gallery và amenity gold không thêm cột nghiệp vụ ngoài bảng nguồn. Timestamp là field hệ thống của gold.
- Ghi MERGE idempotent theo khóa đã chốt. Không INSERT append-only.
- Phần amenity trong mapping tách bạch: hiện trạng silver lấy từ code, rule gold chỉ là 1-1.

## Constraints

- Có `data_model_change`. Trước `run-gate` architecture phải có `model-design.md` qua `run-author --kind model`.
- Không bịa `pl_name`, khóa MERGE, shape JSON `media`, hay cách căn lại bảng field.
- Mapping không ghi pipeline. Mẫu `gld_srv_poi_info` không được dùng để gán pipeline cho ba bảng này.
- Bảng field §1.2 của media đang lệch hàng: nguồn 3P, nguồn partner, kiểu và target không cùng một cột. `is_cover` chỉ ghi "chọn theo order bé nhất", chưa có kiểu boolean, grain, hay giá trị của dòng còn lại. Coi đó là `CONFLICT`. Dừng ở `user_decision` trước model-design và architecture. Không tự dịch hàng.
- Shape `slv_pn_business_service_i18ns.media` và `slv_pn_business_services.media` không có trong repo thì viết probe nhỏ nhất và dừng ở `waiting_evidence`. Không bịa array hay object.
- Registry hiện ghi cả hai cột `media` là `string`. Shape bên trong chuỗi chưa có trong repo. Probe chỉ viết sau khi hết CONFLICT.

## Classification rationale

- Complexity: `high`. Ba bảng mới, union silver, hai gold 1-1, DDL ở cả hai notebook setup, cạnh ctrl, MERGE idempotent, và spec §1.2 chưa căn được.
- Risk: `medium`. Thêm bảng mới. Logic, grain, khóa và cạnh ctrl của `slv_poi_amenity` giữ nguyên. Rollback của bảng mới là drop bảng và xóa cạnh mới. Không phải `high` vì không đổi recovery của bảng đang chạy.
- Architecture: required. Grain và khóa bảng mới, logic silver sang gold, nhiều hơn tám file, và `is_cover` còn nhiều cách đọc. `data_model_change` nên cần `model-design.md` trước Architect. Fast lane không áp dụng.
- Evidence: required. Cột partner `media` chỉ là `string`. Array hay object, và field `url` / `order`, không có trong registry. Grain `media_id` / `media_dedup_key` cũng chưa chốt vì §1.2 lệch hàng. Probe chờ hết CONFLICT.
- Runtime proof: required. DDL, registry và MERGE trên Fabric DEV chưa chứng minh được bằng test local.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`. `risk_gate` không bắt buộc vì risk `medium`. `fabric-pipeline-reviewer` chưa đưa vào: mapping không ghi pipeline và `pl_name` không được suy từ `gld_srv_poi_info`.
